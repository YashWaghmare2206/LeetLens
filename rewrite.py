import sys, re
with open('backend/app/api/v1/router.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('from fastapi import APIRouter, HTTPException, Query', 'from fastapi import APIRouter, HTTPException, Query, Request')

code = re.sub(r'async def get_(\w+)\(username: str\):', r'async def get_\1(username: str, history_key: str | None = None):', code)
code = code.replace('difficulty: str | None = Query(None, description="Filter: Easy | Medium | Hard"),\n):', 'difficulty: str | None = Query(None, description="Filter: Easy | Medium | Hard"),\n    history_key: str | None = None\n):')
code = code.replace('async def get_pattern_detail(username: str, pattern_slug: str):', 'async def get_pattern_detail(username: str, pattern_slug: str, history_key: str | None = None):')

code = re.sub(r'await StatelessService\.get_(\w+)\(username\)', r'await StatelessService.get_\1(username, history_key=history_key)', code)
code = code.replace('await StatelessService.get_pattern_detail(username, pattern_slug)', 'await StatelessService.get_pattern_detail(username, pattern_slug, history_key=history_key)')
code = code.replace('await StatelessService.get_problems(username, difficulty=difficulty)', 'await StatelessService.get_problems(username, difficulty=difficulty, history_key=history_key)')

code = code.replace('if not user:\n        raise HTTPException(status_code=404', 'if not user:\n        if history_key: raise HTTPException(status_code=409, detail="history_expired")\n        raise HTTPException(status_code=404')
code = code.replace('if result is None:\n        raise HTTPException(status_code=404', 'if result is None:\n        if history_key: raise HTTPException(status_code=409, detail="history_expired")\n        raise HTTPException(status_code=404')
code = code.replace('if result is None:\n        raise HTTPException(\n            status_code=404', 'if result is None:\n        if history_key: raise HTTPException(status_code=409, detail="history_expired")\n        raise HTTPException(\n            status_code=404')


with open('backend/app/api/v1/router.py', 'w', encoding='utf-8') as f:
    f.write(code)
