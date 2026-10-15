# Research recommendations

Editorial syntheses, not installed policy.

## AW01

Pinned native checks with honest scope and failure evidence. Strong foundation; maintain fixtures and actual tool-version knowledge

Evidence: [GD02](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html), [GD03](https://raw.githubusercontent.com/godotengine/godot/4.7.2-stable/main/main.cpp), [GD13](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/warning_system.html), [OA07](https://developers.openai.com/blog/eval-skills).

## AW02

Saved-scene/editor inspection plus relevant visible play. Strong foundation; observation takes time and remains bounded

Evidence: [GD10](https://docs.godotengine.org/en/stable/classes/class_node.html), [GD12](https://docs.godotengine.org/en/stable/classes/class_packedscene.html).

## AW03

Focused behavior tests using real scene/resource boundaries. Strong foundation; assertions and test discovery need scrutiny

Evidence: [GD06](https://github.com/bitwes/Gut), [GD07](https://gut.readthedocs.io/en/v9.7.1/Command-Line.html), [GD08](https://github.com/godot-gdunit-labs/gdUnit4/releases/tag/v6.2.2), [GD09](https://github.com/godot-gdunit-labs/gdunit4/blob/master/documentation/doc/_advanced_testing/cmd.md), [EV14](https://arxiv.org/html/2410.21136v1), [EV15](https://arxiv.org/html/2609.09315v1).

## AW04

Small curated procedural Godot skills. Prioritize recurring tasks; evaluate benefit and incorrect activation

Evidence: [OA03](https://learn.chatgpt.com/docs/build-skills), [OA07](https://developers.openai.com/blog/eval-skills), [EV16](https://arxiv.org/html/2602.12670v4), [EV17](https://arxiv.org/html/2602.11988v3).

## AW05

Scoped repository invariants with examples and exceptions. Retain non-obvious consequential knowledge; prevent context inflation

Evidence: [OA04](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [AN04](https://code.claude.com/docs/en/memory), [EV17](https://arxiv.org/html/2602.11988v3), [PK07](https://www.aihero.dev/skills-code-review).

## AW06

Specialists defined by failure surfaces and evidence. Strong candidate for substantive changes; count unique valid findings

Evidence: [EV04](https://aclanthology.org/2024.findings-emnlp.888.pdf), [EV08](https://arxiv.org/html/2607.21656v1), [EV09](https://www.greptile.com/blog/model-inversion), [EV11](https://arxiv.org/html/2608.09290v1), [PK14](https://www.reddit.com/r/claude/comments/1ti1mc3/many_false_positives_in_code_review_using_opus_47/).

## AW07

Fresh-context review with necessary project evidence. Good candidate for consequential changes; avoid stripping useful context

Evidence: [AN10](https://www.anthropic.com/engineering/harness-design-long-running-apps), [EV05](https://arxiv.org/pdf/2310.01798), [PK07](https://www.aihero.dev/skills-code-review), [PK12](https://www.reddit.com/r/ClaudeAI/comments/1vv7pdk/codex_writes_claude_code_reviews_heres_how_it_went/).

## AW08

Separate requirements and standards judgments. Useful distinction; both inputs must be authoritative and findable

Evidence: [PK07](https://www.aihero.dev/skills-code-review), [PK17](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md).

## AW09

Deterministic triggers and externally enforced acceptance. Test actual event, failure, absence, identity, and bypass semantics

Evidence: [OA02](https://learn.chatgpt.com/docs/hooks), [AN02](https://code.claude.com/docs/en/hooks), [PK04](https://git-scm.com/docs/githooks), [PK05](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [PK06](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).

## AW10

Selected deliberate defects to validate important checks. Valuable calibration; mutation must be meaningful and safely isolated later

Evidence: [EV14](https://arxiv.org/html/2410.21136v1), [EV15](https://arxiv.org/html/2609.09315v1), [PK12](https://www.reddit.com/r/ClaudeAI/comments/1vv7pdk/codex_writes_claude_code_reviews_heres_how_it_went/), [PK15](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/), [PK16](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/).

## AW11

Ratchet existing debt rather than fail everything. Useful on established projects; metrics and exceptions need ownership

Evidence: [PK10](https://github.com/svetdev/cleat), [PK11](https://www.reddit.com/r/ClaudeCode/comments/1w6i5f4/havent_written_code_by_hand_all_year_heres_what_i/).

## AW12

Parallel work on substantial independent tasks. Use when coordination savings exceed integration and context cost

Evidence: [OA01](https://learn.chatgpt.com/docs/agent-configuration/subagents), [AN01](https://code.claude.com/docs/en/sub-agents), [EV07](https://arxiv.org/html/2512.08296v1), [PK08](https://www.aihero.dev/skills-implement-spec).

## AW13

Different-family review on selected risky changes. Experiment rather than mandate; pairing can help or harm

Evidence: [EV08](https://arxiv.org/html/2607.21656v1), [EV09](https://www.greptile.com/blog/model-inversion), [PK12](https://www.reddit.com/r/ClaudeAI/comments/1vv7pdk/codex_writes_claude_code_reviews_heres_how_it_went/), [PK13](https://www.reddit.com/r/claudeskills/comments/1wujndt/codex_made_my_code_review_worse/).

## AW14

MCP-assisted engine/editor observation. Optional aid; verify saved/runtime outcomes and compatibility

Evidence: [GD17](https://github.com/satelliteoflove/godot-mcp/blob/main/docs/tools/README.md).

## AW15

Representative performance and export checks. Important when affected; target and measurement conditions matter

Evidence: [GD14](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/the_profiler.html), [GD15](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html).

## AW16

Universal complexity/coverage/mutation thresholds. Weak default; cannot substitute for relevant behavior or maintainability

Evidence: [EV14](https://arxiv.org/html/2410.21136v1), [EV15](https://arxiv.org/html/2609.09315v1), [RM02](https://github.com/unclebob/negative-test-experiment/blob/main/experiment-conclusion.md), [PK16](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/).

## AW17

Persona names or celebrity imitation without concrete duties. Weak assurance value; tone is not expertise

Evidence: [EV04](https://aclanthology.org/2024.findings-emnlp.888.pdf).

## AW18

Debate, vote count, or unbounded repeated review as approval. Poor sole acceptance criterion; evidence should settle findings

Evidence: [EV06](https://proceedings.neurips.cc/paper_files/paper/2025/file/934252acd87f254d5d4672fbde283bd2-Paper-Conference.pdf), [EV07](https://arxiv.org/html/2512.08296v1), [PK07](https://www.aihero.dev/skills-code-review).
