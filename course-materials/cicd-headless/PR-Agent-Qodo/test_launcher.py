"""Run the real launcher with a fake Docker executable; no network or secrets."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).parent
SCRIPT = HERE / "review-pr.sh"
CLI_IMAGE = "pragent/pr-agent:0.47.0@sha256:7d98954c29289846a08faf00aaea0f1f1375b1676cd8a2ed303e0af07010af7a"
PLATFORM_FILES = ["github-actions.yml", "gitlab-ci.yml", "bitbucket-pipelines.yml", "azure-pipelines.yml",
                  "gitea-actions.yml", "Jenkinsfile", "bamboo-specs.yaml"]
GITHUB = ("github", "https://github.com/training/demo/pull/7", {"GITHUB__USER_TOKEN": "secret"})


class LauncherContracts(unittest.TestCase):
    def run_launcher(self, provider, url, extra=None, command="review"):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docker = root / "docker"
            docker.write_text('#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
            docker.chmod(0o755)
            env = {"PATH": folder + ":" + os.environ["PATH"],
                   "PR_AGENT_IMAGE": "pragent/pr-agent@sha256:" + "a" * 64,
                   "GIT_PLATFORM": provider, "PR_URL": url,
                   "REVIEW_API_KEY": "synthetic-secret"}
            env.update(extra or {})
            return subprocess.run(["bash", str(SCRIPT), command], env=env, capture_output=True, text=True)

    def test_supported_platforms_forward_names_and_cli_command(self):
        fixtures = [
            GITHUB,
            ("gitlab", "https://gitlab.example.com/team/demo/-/merge_requests/7",
             {"GITLAB__URL": "https://gitlab.example.com", "GITLAB__PERSONAL_ACCESS_TOKEN": "secret"}),
            ("bitbucket", "https://bitbucket.org/training/demo/pull-requests/7", {"BITBUCKET__BEARER_TOKEN": "secret"}),
            ("bitbucket_server", "https://git.example.com/projects/COURSE/repos/demo/pull-requests/7",
             {"BITBUCKET_SERVER__URL": "https://git.example.com", "BITBUCKET_SERVER__BEARER_TOKEN": "secret"}),
            ("azure", "https://dev.azure.com/training/course/_git/demo/pullrequest/7",
             {"AZURE_DEVOPS__ORG": "https://dev.azure.com/training", "AZURE_DEVOPS__PAT": "secret"}),
            ("gitea", "https://gitea.example.com/training/demo/pulls/7",
             {"GITEA__URL": "https://gitea.example.com", "GITEA__PERSONAL_ACCESS_TOKEN": "secret"}),
        ]
        for provider, url, extra in fixtures:
            with self.subTest(provider=provider):
                result = self.run_launcher(provider, url, extra)
                self.assertEqual(result.returncode, 0, result.stderr)
                args = json.loads(result.stdout)
                self.assertEqual(args[-5:], ["-m", "pr_agent.cli", "--pr_url", url, "review"])
                self.assertIn(f"CONFIG__GIT_PROVIDER={provider}", args)
                self.assertIn("CONFIG__PROPAGATE_TOOL_ERRORS=true", args)
                self.assertNotIn("synthetic-secret", result.stdout)
                self.assertNotIn("=secret", result.stdout)

    def test_defaults_target_openrouter_and_luna_with_the_review_budget(self):
        result = self.run_launcher(*GITHUB)
        self.assertEqual(result.returncode, 0, result.stderr)
        args = json.loads(result.stdout)
        for expected in ("OPENAI__API_BASE=https://openrouter.ai/api/v1",
                         "CONFIG__MODEL=openai/openai/gpt-6-luna",
                         'CONFIG__NO_TEMPERATURE_MODELS=["openai/openai/gpt-6-luna"]',
                         'CONFIG__ADDITIONAL_REASONING_EFFORT_MODELS=["openai/openai/gpt-6-luna"]',
                         "CONFIG__REASONING_EFFORT=low",
                         "CONFIG__CUSTOM_MODEL_MAX_TOKENS=250000", "CONFIG__MAX_MODEL_TOKENS=250000",
                         "PR_REVIEWER__ENABLE_LARGE_PR_CHUNKING=true", "PR_REVIEWER__MAX_NUMBER_OF_CALLS=4",
                         "CONFIG__FALLBACK_MODELS=[]", "CONFIG__PUBLISH_OUTPUT=false"):
            self.assertIn(expected, args)
        # The key travels by variable name only.
        self.assertIn("OPENAI__KEY", args)
        self.assertFalse([a for a in args if a.startswith("OPENAI__KEY=")])

    def test_endpoint_model_budget_and_dry_run_are_configurable(self):
        provider, url, extra = GITHUB
        result = self.run_launcher(provider, url, {
            **extra, "REVIEW_API_BASE": "https://training.openai.azure.com/openai/v1",
            "REVIEW_MODEL": "course-review-luna", "REVIEW_MAX_TOKENS": "1000000",
            "REVIEW_PUBLISH": "true", "REVIEW_REASONING_EFFORT": "none"})
        self.assertEqual(result.returncode, 0, result.stderr)
        args = json.loads(result.stdout)
        self.assertIn("OPENAI__API_BASE=https://training.openai.azure.com/openai/v1", args)
        self.assertIn("CONFIG__MODEL=openai/course-review-luna", args)
        self.assertIn("CONFIG__MAX_MODEL_TOKENS=1000000", args)
        self.assertIn("CONFIG__PUBLISH_OUTPUT=true", args)
        self.assertFalse([a for a in args if a.startswith("CONFIG__REASONING_EFFORT=")])

    def test_invalid_input_never_starts_docker(self):
        provider, url, token = GITHUB
        cases = [({}, "push"),
                 ({"PR_URL": "https://attacker.invalid/pull/7"}, "review"),
                 ({"PR_AGENT_IMAGE": "pragent/pr-agent:latest"}, "review"),
                 ({"REVIEW_API_KEY": ""}, "review"),
                 ({"REVIEW_API_BASE": "http://openrouter.ai/api/v1"}, "review"),
                 ({"REVIEW_API_BASE": "https://user:pw@example.com/v1"}, "review"),
                 ({"REVIEW_MODEL": 'x"],"y'}, "review"),
                 ({"REVIEW_MAX_TOKENS": "9999999"}, "review"),
                 ({"REVIEW_MAX_TOKENS": "lots"}, "review"),
                 ({"REVIEW_PUBLISH": "maybe"}, "review"),
                 ({"REVIEW_REASONING_EFFORT": "extreme"}, "review")]
        for overrides, command in cases:
            with self.subTest(overrides=overrides, command=command):
                result = self.run_launcher(provider, url, {**token, **overrides}, command)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")


class PlatformFileContracts(unittest.TestCase):
    """Every platform example exposes the same endpoint variables and a pinned runtime."""

    def test_each_platform_file_uses_the_shared_variables(self):
        for name in PLATFORM_FILES:
            with self.subTest(name=name):
                text = (HERE / name).read_text(encoding="utf-8")
                for variable in ("REVIEW_API_KEY", "REVIEW_API_BASE", "REVIEW_MODEL", "REVIEW_MAX_TOKENS"):
                    self.assertIn(variable, text)
                self.assertIn("openrouter.ai/api/v1", text)
                self.assertIn("openai/gpt-6-luna", text)
                self.assertIn("@sha256:", text)
                self.assertNotIn(":latest", text)
                self.assertNotIn("ANTHROPIC", text)

    def test_files_that_call_pr_agent_directly_set_the_model_safeguards(self):
        # Jenkins and Bamboo delegate to review-pr.sh, which the launcher tests cover.
        for name in ("github-actions.yml", "gitlab-ci.yml", "bitbucket-pipelines.yml",
                     "azure-pipelines.yml", "gitea-actions.yml"):
            with self.subTest(name=name):
                text = (HERE / name).read_text(encoding="utf-8")
                for setting in ("CONFIG__NO_TEMPERATURE_MODELS", "CONFIG__ADDITIONAL_REASONING_EFFORT_MODELS",
                                "CONFIG__CUSTOM_MODEL_MAX_TOKENS", "CONFIG__MAX_MODEL_TOKENS",
                                "CONFIG__FALLBACK_MODELS", "CONFIG__PROPAGATE_TOOL_ERRORS",
                                "PR_REVIEWER__ENABLE_LARGE_PR_CHUNKING", "PR_REVIEWER__MAX_NUMBER_OF_CALLS"):
                    self.assertIn(setting, text)
                self.assertIn(CLI_IMAGE, text)

    def test_launcher_based_pipelines_fix_the_endpoint_and_publish_explicitly(self):
        # A build parameter or plan variable for the endpoint would let a build user redirect the API key.
        jenkins = (HERE / "Jenkinsfile").read_text(encoding="utf-8")
        self.assertNotIn("parameters {", jenkins)
        self.assertIn("environment {", jenkins)
        bamboo = (HERE / "bamboo-specs.yaml").read_text(encoding="utf-8")
        self.assertNotIn("bamboo_REVIEW_API_BASE", bamboo)
        self.assertNotIn("bamboo_REVIEW_API_KEY_PASSWORD", bamboo)
        self.assertIn("environment: REVIEW_API_KEY=${bamboo.REVIEW_API_KEY_PASSWORD}", bamboo)
        # Bamboo only imports bamboo-specs/bamboo.yaml and must not schedule the job on an unprepared agent.
        self.assertIn("bamboo-specs/bamboo.yaml", bamboo)
        self.assertIn("requirements:\n    - pr-agent-review", bamboo)
        for text in (jenkins, bamboo):
            self.assertRegex(text, r"REVIEW_PUBLISH\s*=\s*'?true")

    def test_yaml_examples_parse(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML is not installed")
        for name in PLATFORM_FILES:
            if name == "Jenkinsfile":
                continue
            with self.subTest(name=name):
                self.assertIsInstance(yaml.safe_load((HERE / name).read_text(encoding="utf-8")), dict)

    def test_readme_links_every_platform_file(self):
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        for name in PLATFORM_FILES + ["review-pr.sh"]:
            self.assertIn(f"]({name})", readme, name)


if __name__ == "__main__":
    unittest.main()
