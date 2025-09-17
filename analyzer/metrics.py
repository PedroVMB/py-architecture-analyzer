import os
import ast
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.visitors import ComplexityVisitor
from collections import defaultdict

# ---- Helpers para varrer projeto e filtrar arquivos de código (python por ora) ----
def list_python_files(root):
    py_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.py'):
                py_files.append(os.path.join(dirpath, f))
    return py_files

def count_loc(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            if f.endswith('.py'):
                fp = os.path.join(dirpath, f)
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                    lines = fh.readlines()
                    # excluir linhas vazias e comentários simples?
                    total += len(lines)
    return total

def ast_counts(py_files):
    """
    Retorna dict com número de classes, funções por projeto e por arquivo.
    """
    counts = {'classes':0, 'functions':0, 'modules':len(py_files), 'by_file':{}}
    for f in py_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                src = fh.read()
            tree = ast.parse(src)
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            counts['classes'] += len(classes)
            counts['functions'] += len(funcs)
            counts['by_file'][f] = {'classes':len(classes), 'functions':len(funcs)}
        except Exception:
            counts['by_file'][f] = {'classes':0, 'functions':0}
    return counts

def complexity_metrics(py_files):
    """
    Usa radon para gerar complexidade por função/classe e índice de mantenabilidade (MI).
    Retorna média de CC por arquivo, MI médio.
    """
    cc_values = []
    mi_values = []
    for p in py_files:
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                src = fh.read()
            # CC
            blocks = cc_visit(src)
            for b in blocks:
                cc_values.append(b.complexity)
            # MI
            mi = mi_visit(src, True)
            mi_values.append(mi)
        except Exception:
            continue
    avg_cc = sum(cc_values)/len(cc_values) if cc_values else 0
    avg_mi = sum(mi_values)/len(mi_values) if mi_values else 0
    return {'avg_cc': avg_cc, 'avg_mi': avg_mi, 'num_cc_blocks': len(cc_values)}

# heurística simples de acoplamento: contar imports entre arquivos do projeto
def coupling_metric(py_files, project_root):
    """
    Conta quantas vezes um arquivo importa outro arquivo do mesmo projeto (por nome de módulo relativo).
    Retorna número absoluto e média por arquivo.
    """
    imports = defaultdict(int)
    module_lookup = {}
    for f in py_files:
        rel = os.path.relpath(f, project_root)
        module_name = rel.replace(os.sep, '.')[:-3]  # remove .py
        module_lookup[module_name] = f
    total_links = 0
    for f in py_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                src = fh.read()
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        name = n.name
                        # se começa com algum módulo do projeto, conta
                        for mod in module_lookup:
                            if name.startswith(mod):
                                total_links += 1
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ''
                    for known in module_lookup:
                        if mod.startswith(known):
                            total_links += 1
        except Exception:
            continue
    avg_links = total_links / len(py_files) if py_files else 0
    return {'total_import_links': total_links, 'avg_links_per_file': avg_links}

# heurística simples de separação de domínio:
def domain_separation_heuristic(project_root):
    """
    Busca pastas/arquivos com nomes de domínio comuns: 'order', 'order_service', 'payment', 'catalog', 'customer'
    Retorna contagem dessas pastas e arquivos.
    """
    keywords = ['order','pedido','payment','pagamento','catalog','catalogo','product','produto','cart','carrinho','customer','cliente','inventory','estoque','shipping','logistics','checkout']
    found = []
    for dirpath, dirnames, filenames in os.walk(project_root):
        base = os.path.basename(dirpath).lower()
        if any(k in base for k in keywords):
            found.append(dirpath)
        for f in filenames:
            name = f.lower()
            if any(k in name for k in keywords):
                found.append(os.path.join(dirpath, f))
    unique = list(set(found))
    return {'domain_segments': len(unique), 'examples': unique[:10]}

# função agregadora
def analyze_project(project_root):
    py_files = list_python_files(project_root)
    loc = count_loc(project_root)
    ast_info = ast_counts(py_files)
    complexity = complexity_metrics(py_files)
    coupling = coupling_metric(py_files, project_root)
    domain = domain_separation_heuristic(project_root)
    return {
        'path': project_root,
        'num_py_files': len(py_files),
        'loc': loc,
        'ast': ast_info,
        'complexity': complexity,
        'coupling': coupling,
        'domain': domain
    }
