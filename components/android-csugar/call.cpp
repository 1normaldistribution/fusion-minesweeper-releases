// Adapts the original managed CSPCore Call(string) protocol to upstream CSugar.
// CSugar's parser, encoder, graph constraints and SAT solver are unchanged.
#define main csugar_command_line_main
#include "upstream/csugar/src/main.cpp"
#undef main
#include <sstream>
#include <stdexcept>

static std::string reply;
static std::string last_error;
extern "C" const char* csugar_last_error() { return last_error.c_str(); }
extern "C" void csugar_clear_error() { last_error.clear(); }

static void Maximal(IntegratedCSPSolver& solver, const std::vector<std::string>& keys, std::ostream& output) {
    for (const auto& key : keys) if (!solver.HasBoolVar(key)) throw std::runtime_error("Local maximal requires Boolean answer keys");
    solver.SetTargetVars(keys);
    auto answer = solver.Solve();
    if (!answer.IsSat()) { output << "unsat\n"; return; }
    // Preserve true keys, then ask whether any remaining false key can be true.
    while (true) {
        std::vector<std::shared_ptr<Expr>> improve;
        for (const auto& key : keys) {
            auto expr = Expr::VarBool(solver.GetBoolVar(key));
            if (answer.GetBool(key)) solver.AddConstraint(expr);
            else improve.push_back(expr);
        }
        if (improve.empty()) break;
        solver.AddConstraint(std::make_shared<Expr>(kOr, improve));
        auto next = solver.Solve();
        if (!next.IsSat()) break;
        answer = std::move(next);
    }
    output << "sat\n";
    // Original DLL intentionally reports false keys only in $-2 mode.
    for (const auto& key : keys) if (!answer.GetBool(key)) output << key << " false\n";
}

static void Enumerate(IntegratedCSPSolver& solver, const std::vector<std::string>& keys, int maximum, std::ostream& output) {
    solver.SetTargetVars(keys);
    for (int index=0; maximum<0 || index<maximum; ++index) {
        auto answer = solver.Solve();
        if (!answer.IsSat()) break;
        output << "ans " << index << '\n';
        std::vector<std::shared_ptr<Expr>> differ;
        for (const auto& key : keys) {
            if (solver.HasBoolVar(key)) {
                bool value=answer.GetBool(key);
                output << key << ' ' << (value?"true":"false") << '\n';
                differ.push_back(Expr::Make(kXor,{Expr::VarBool(solver.GetBoolVar(key)),Expr::ConstBool(value)}));
            } else {
                int value=answer.GetInt(key);output << key << ' ' << value << '\n';
                differ.push_back(Expr::Make(kNe,{Expr::VarInt(solver.GetIntVar(key)),Expr::ConstInt(value)}));
            }
        }
        output << "$\n";
        solver.AddConstraint(std::make_shared<Expr>(kOr,differ));
    }
    output << "unsat\n"; // Original protocol's end-of-enumeration marker.
}

extern "C" const char* Call(const char* query) {
    last_error.clear();
    try {
        std::istringstream source(query?query:""); std::ostringstream csp,output;std::string line;
        int mode=0,maximum=0;
        while (std::getline(source,line)) {
            if (!line.empty() && line.back()=='\r') line.pop_back();
            if (line=="?") break;
            if (!line.empty() && line[0]=='$') { maximum=std::stoi(line.substr(1));mode=maximum==-2?2:1; }
            else csp << line << '\n';
        }
        IntegratedCSPSolver solver;bool keyed=false;std::vector<std::string> keys;std::istringstream body(csp.str());
        InputCSP(solver,keyed,keys,body);
        if (!keyed) FindAnswer(solver,output);
        else if (mode==2) Maximal(solver,keys,output);
        else if (mode==1) Enumerate(solver,keys,maximum,output);
        else SolveIrrefutably(solver,keys,output);
        reply=output.str();
    } catch (const std::exception& error) { last_error=error.what();reply="s ERROR\n"; }
    return reply.c_str();
}
