import os

from gptchain.logger import logger

# Default gptchain.md file created if none exists
DEFAULT_MARKDOWN_STR = """# Welcome to gptchain! 🚀🤖

Hi there, Developer! 👋 We're excited to have you on board. gptchain is a powerful tool designed to help you prototype, debug and share applications built on top of LLMs.

## Useful Links 🔗

- **Documentation:** Get started with our comprehensive [gptchain Documentation](https://docs.gptchain.io) 📚
- **Discord Community:** Join our friendly [gptchain Discord](https://discord.gg/k73SQ3FyUh) to ask questions, share your projects, and connect with other developers! 💬

We can't wait to see what you create with gptchain! Happy coding! 💻😊

## Welcome screen

To modify the welcome screen, edit the `gptchain.md` file at the root of your project. If you do not want a welcome screen, just leave this file empty.
"""


def init_markdown(root: str):
    """Initialize the gptchain.md file if it doesn't exist."""
    gptchain_md_file = os.path.join(root, "gptchain.md")

    if not os.path.exists(gptchain_md_file):
        with open(gptchain_md_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_MARKDOWN_STR)
            logger.info(f"Created default gptchain markdown file at {gptchain_md_file}")


def get_markdown_str(root: str):
    """Get the gptchain.md file as a string."""
    gptchain_md_path = os.path.join(root, "gptchain.md")
    if os.path.exists(gptchain_md_path):
        with open(gptchain_md_path, "r", encoding="utf-8") as f:
            gptchain_md = f.read()
            return gptchain_md
    else:
        return None
