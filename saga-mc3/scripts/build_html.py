import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
caps = json.loads((root / "assets/captions.json").read_text())
src = (root / "source/index.template.html").read_text()
out = src.replace("/*CAPTIONS*/[]", json.dumps(caps, ensure_ascii=False, separators=(",", ":")))
(root / "index.html").write_text(out)
print("index.html written", len(out))
