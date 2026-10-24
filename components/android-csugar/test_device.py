"""Run synthetic CSP checks on a connected ARM64 Android device, without a game install."""
from pathlib import Path
import argparse, json, subprocess, uuid

HERE = Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb',default='adb')
    parser.add_argument('--build',type=Path,default=HERE/'build')
    parser.add_argument('--serial')
    args=parser.parse_args()
    command=[args.adb]+(['-s',args.serial] if args.serial else [])
    def adb(*parameters,data=None):
        result=subprocess.run(command+list(parameters),input=data,capture_output=True,timeout=45)
        if result.returncode:raise RuntimeError(result.stderr.decode('utf-8',errors='replace'))
        return result.stdout.decode('utf-8',errors='replace').replace('\r','')
    remote='/data/local/tmp/csugar-component-'+uuid.uuid4().hex
    adb('shell','mkdir',remote)
    results=[]
    def solve(name,query,check):
        output=adb('shell','-T','env','LD_LIBRARY_PATH='+remote,remote+'/solver-cli',data=query.encode())
        if not check(output):raise AssertionError(name+': '+output)
        results.append({'name':name,'passed':True,'output':output})
    try:
        for name in ('libcsugar.so','solver-cli'):adb('push',str(args.build/name),remote+'/'+name)
        adb('shell','chmod','700',remote+'/solver-cli')
        solve('clue-inference',(HERE/'examples/clue-inference.csp').read_text(),lambda s:all(x in s.splitlines() for x in ('sat','a false','b true','c false')))
        solve('ambiguous-not-forced','(bool a)\n(bool b)\n(xor a b)\n# a b\n?\n',lambda s:s.strip()=='sat')
        solve('contradiction','(bool a)\n(and a (not a))\n# a\n?\n',lambda s:s.strip()=='unsat')
        solve('integer-forced','(int n 0 2)\n(= n 2)\n# n\n?\n',lambda s:s.strip()=='sat\nn 2')
        solve('enumerate-two-solutions','(bool a)\n(bool b)\n(xor a b)\n# a b\n$2\n?\n',lambda s:s.count('ans ')==2 and 'a true' in s and 'a false' in s and s.rstrip().endswith('unsat'))
        solve('local-maximal','(bool a)\n(bool b)\n(xor a b)\n# a b\n$-2\n?\n',lambda s:s.startswith('sat\n') and s.count(' false')==1 and ' true' not in s)
        # Parse errors must propagate to the caller rather than becoming a valid answer.
        error=subprocess.run(command+['shell','-T','env','LD_LIBRARY_PATH='+remote,remote+'/solver-cli'],input=b'(unknown a)\n?\n',capture_output=True,timeout=45)
        if error.returncode==0:raise AssertionError('Invalid input was accepted')
        results.append({'name':'invalid-input-error','passed':True})
        report={'passed':True,'scope':'synthetic CSP protocol tests on Android ARM64','cases':results}
        (args.build/'device-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False))
    finally:
        # Only this test's three files and its unique directory are removed.
        adb('shell','rm','-f',remote+'/libcsugar.so',remote+'/solver-cli')
        adb('shell','rmdir',remote)

if __name__=='__main__':main()
