"""Build the extracted Android solver without the game, .NET or original puzzles."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, os, platform, subprocess, sys
import urllib.request, zipfile, io

HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(lock, destination):
    for name in ('csugar', 'glucose'):
        pin = lock[name]
        required = {k.split('/', 1)[1]: v for k, v in lock['files'].items() if k.startswith(name + '/')}
        if all((destination/name/k).is_file() and digest(destination/name/k) == v for k,v in required.items()):
            continue
        url = pin['url'].replace('https://github.com/', 'https://codeload.github.com/') + '/zip/' + pin['commit']
        print('Fetching pinned ' + name, flush=True)
        with urllib.request.urlopen(url, timeout=120) as response:
            archive = zipfile.ZipFile(io.BytesIO(response.read()))
        prefix = name + '-' + pin['commit'] + '/'
        # Read only explicitly locked files. Never extract arbitrary archive paths.
        for relative, expected in required.items():
            target = (destination/name/relative).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise RuntimeError('Invalid locked path: ' + relative)
            data = archive.read(prefix + relative)
            if hashlib.sha256(data).hexdigest() != expected:
                raise RuntimeError('Upstream hash mismatch: ' + name + '/' + relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ndk', required=True, type=Path, help='Official Android NDK directory (tested: r27c)')
    parser.add_argument('--upstream', type=Path, help='Optional pre-populated csugar/glucose directory; all locked inputs are verified')
    parser.add_argument('--output', type=Path, default=HERE/'build')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    lock = json.loads((HERE/'upstream-lock.json').read_text(encoding='utf-8'))
    upstream = (args.upstream or HERE/'upstream').resolve()
    if not args.upstream:
        prepare(lock, upstream)
    for name, expected in lock['files'].items():
        source = (upstream/name).resolve()
        if not source.is_relative_to(upstream) or not source.is_file() or digest(source) != expected:
            raise RuntimeError('Missing or changed pinned input: ' + name)
    host = {'win32':'windows-x86_64', 'linux':'linux-x86_64', 'darwin':'darwin-x86_64'}.get(sys.platform)
    if not host:
        raise RuntimeError('Unsupported build host: ' + sys.platform)
    clang = args.ndk.resolve()/'toolchains/llvm/prebuilt'/host/'bin'/('clang++.exe' if os.name == 'nt' else 'clang++')
    if not clang.is_file():
        raise RuntimeError('Official NDK clang++ not found: ' + str(clang))
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    flags = ['--target=aarch64-linux-android23','-std=c++17','-O3','-DNDEBUG','-DUSE_GLUCOSE','-fPIC','-fexceptions','-frtti',
             '-I'+str(HERE/'include'),'-I'+str(upstream/'csugar/include'),'-I'+str(upstream/'glucose'),'-I'+str(upstream.parent)]
    sources = [p for sub in ('common','conv','csp','icsp','integrated','sat') for p in sorted((upstream/'csugar/src'/sub).glob('*.cpp'))]
    sources += sorted((upstream/'glucose/core').glob('*.cc')) + sorted((upstream/'glucose/utils').glob('*.cc'))
    sources += [upstream/'glucose/simp/SimpSolver.cc', HERE/'call.cpp']
    def run(command):
        result = subprocess.run([str(v) for v in command], capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    def compile_one(source):
        target = output/(hashlib.sha256(str(source).encode()).hexdigest()[:16]+'.o')
        stamp = target.with_suffix('.sha256')
        signature = hashlib.sha256(source.read_bytes() + json.dumps(flags).encode() + (HERE/'upstream-lock.json').read_bytes()
                    + (args.ndk/'source.properties').read_bytes() + Path(__file__).read_bytes() + (HERE/'include/fpu_control.h').read_bytes()).hexdigest()
        if not target.exists() or not stamp.exists() or stamp.read_text() != signature:
            run([clang,*flags,'-c',source,'-o',target]); stamp.write_text(signature)
        return target
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
        objects = list(pool.map(compile_one, sources))
    library = output/'libcsugar.so'
    common = [clang,'--target=aarch64-linux-android23','-static-libstdc++','-Wl,-z,max-page-size=16384']
    run([*common,'-shared','-Wl,-soname,libcsugar.so',*objects,'-lz','-llog','-o',library])
    run([*common,HERE/'solver_cli.cpp','-L'+str(output),'-lcsugar','-Wl,-rpath,$ORIGIN','-o',output/'solver-cli'])
    report = {'abi':'arm64-v8a','minimumApi':23,'pageAlignment':16384,'sourceFiles':len(sources),
              'librarySha256':digest(library),'cliSha256':digest(output/'solver-cli'),
              'ndk':(args.ndk/'source.properties').read_text().strip()}
    (output/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)

if __name__ == '__main__':
    main()
