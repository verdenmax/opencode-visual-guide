"""Shared 'work in progress' placeholder for lessons not yet written.

Each content milestone (M1-M12) replaces its part's `LESSON_NN = wip(...)`
entries with real bilingual content dicts. The placeholder is intentionally
>80 chars per language (so check_html ERROR passes) but lacks analogy/key-points
cards and diagrams (so it WARNs - a built-in "unfinished" dashboard).
"""


def wip(zh_title, en_title):
    return {
        "zh": (
            f'<p class="lead">本课《{zh_title}》正在建设中，敬请期待。</p>'
            f'<div class="card macro"><div class="tag">🚧 建设中</div>'
            f'这一课会逐步拆解 opencode 中“{zh_title}”这一主题，配上图解、'
            f'简化自源码的真实代码引用与自测题。</div>'
        ),
        "en": (
            f'<p class="lead">This lesson "{en_title}" is under construction.</p>'
            f'<div class="card macro"><div class="tag">🚧 WIP</div>'
            f'It will break down the "{en_title}" topic in opencode, with diagrams, '
            f'simplified real source references and a self-test.</div>'
        ),
    }
