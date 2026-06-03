import json
import os
from importlib import metadata
def ensure_deps(req_file):
    '''检查必要依赖'''
    miss_pkg=[]
    with open(req_file,encoding='utf-8',mode='r') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#"):
                continue
            pkg=line.split("==")[0].split(">=")[0].split("<=")[0]
            try:
                metadata.version(pkg)
            except metadata.PackageNotFoundError:
                miss_pkg.append(pkg)
    return miss_pkg
if __name__ == "__main__":
    req_file=os.path.join(os.getcwd(),'requirements.txt')
    miss_pkg=ensure_deps(req_file=req_file)
    output_json=json.dumps({'missing_package':miss_pkg},indent=2)
    print(output_json)