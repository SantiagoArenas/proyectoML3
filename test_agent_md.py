import re
import unittest
from pathlib import Path


def has_frontmatter(text: str) -> bool:
    return bool(re.match(r"\A---\n.*?\n---\n", text, flags=re.DOTALL))


class AgentMdValidationTests(unittest.TestCase):
    def test_agent_md_exists(self):
        self.assertTrue(Path("agent.md").exists(), "agent.md no existe")

    def test_agent_md_has_frontmatter_and_sections(self):
        text = Path("agent.md").read_text(encoding="utf-8")
        self.assertTrue(has_frontmatter(text), "Falta frontmatter YAML")
        for section in ["# Objetivo", "# Datos", "# Metodología", "# Evaluación", "# Entregables"]:
            self.assertIn(section, text, f"Falta sección: {section}")

    def test_negative_missing_section(self):
        broken = "---\nname: x\ndescription: y\n---\n\n# Objetivo\n"
        self.assertNotIn("# Entregables", broken)


if __name__ == "__main__":
    unittest.main()
