# Reference refresh + regression corpus
1. `node .pine-agent/tools/refresh/refresh_reference.mjs /tmp/pine_ref`
2. `python .pine-agent/tools/refresh/build_ledger.py /tmp/pine_ref --date YYYY-MM-DD`
3. Regression: `python .pine-agent/tools/pine_static_check.py /tmp/pine_ref/corpus/*.pine` must report 0 STATIC-FAIL;
   mutation test: `python .pine-agent/tools/refresh/mutation_eval.py /tmp/pine_ref/corpus`.
The corpus is TradingView-authored example code: regenerate locally, do not commit.
