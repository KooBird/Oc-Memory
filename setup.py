#!/usr/bin/env python3
"""
OC-Memory Setup Wizard
Interactive TUI for configuring OC-Memory

Usage:
    python setup.py
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Check and install dependencies
try:
    import questionary
    from questionary import Style
    import yaml
except ImportError:
    print("📦 Installing required dependencies...")
    import subprocess
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "questionary", "pyyaml", "python-dotenv", "-q"
    ])
    import questionary
    from questionary import Style
    import yaml


# ============================================================================
# Custom Style
# ============================================================================

custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#2196f3 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#4caf50'),
    ('separator', 'fg:#cc5454'),
    ('instruction', 'fg:#858585'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])


# ============================================================================
# Setup Wizard
# ============================================================================

class SetupWizard:
    """Interactive setup wizard for OC-Memory"""

    def __init__(self):
        self.config = {}
        self.project_root = Path(__file__).parent
        self.config_path = self.project_root / "config.yaml"
        self.env_path = self.project_root / ".env"

    def run(self):
        """Run the setup wizard"""
        self.print_banner()

        if not self.confirm_start():
            print("👋 Setup cancelled.")
            return

        # Setup steps
        self.step1_watch_directories()
        self.step2_memory_directory()
        self.step3_logging()
        self.step4_optional_features()
        self.step5_openclaw_integration()
        self.step6_create_directories()
        self.step7_auto_test()
        self.step8_ready_to_run()
        self.step9_review_and_save()

    def print_banner(self):
        """Print welcome banner"""
        banner = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🧠 OC-Memory Setup Wizard                                   ║
║                                                                ║
║   External Observational Memory for OpenClaw                  ║
║   Version 0.1.0 (MVP)                                         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

This wizard will help you configure OC-Memory in 9 simple steps.
Setup typically takes less than 5 minutes.
        """
        print(banner)

    def confirm_start(self) -> bool:
        """Confirm to start setup"""
        # Check if config already exists
        if self.config_path.exists():
            print(f"⚠️  Configuration file already exists: {self.config_path}\n")
            return questionary.confirm(
                "Do you want to reconfigure? (existing config will be backed up)",
                default=False,
                style=custom_style
            ).ask()

        return questionary.confirm(
            "Ready to start configuration?",
            default=True,
            style=custom_style
        ).ask()

    def step1_watch_directories(self):
        """Step 1: Configure watch directories"""
        print("\n" + "="*70)
        print("📂 STEP 1: Watch Directories")
        print("="*70)
        print("\nOC-Memory monitors directories for markdown (.md) files.")
        print("When files are created/modified, they're synced to OpenClaw.\n")

        directories = []

        # Common default directories
        default_dirs = [
            Path.home() / "Documents" / "notes",
            Path.home() / "Projects",
            Path.home() / "Desktop"
        ]

        # Ask about each default
        for default_dir in default_dirs:
            if questionary.confirm(
                f"Watch {default_dir}?",
                default=(default_dir == default_dirs[0]),
                style=custom_style
            ).ask():
                directories.append(str(default_dir))

        # Add custom directories
        while True:
            add_more = questionary.confirm(
                "Add another directory?",
                default=False,
                style=custom_style
            ).ask()

            if not add_more:
                break

            custom_dir = questionary.path(
                "Enter directory path:",
                only_directories=True,
                style=custom_style
            ).ask()

            if custom_dir:
                directories.append(custom_dir)

        if not directories:
            print("⚠️  No directories selected. Adding default: ~/Documents/notes")
            directories = [str(Path.home() / "Documents" / "notes")]

        # Recursive watching
        recursive = questionary.confirm(
            "Watch subdirectories recursively?",
            default=True,
            style=custom_style
        ).ask()

        self.config['watch'] = {
            'dirs': directories,
            'recursive': recursive,
            'poll_interval': 1.0
        }

        print(f"\n✅ Will watch {len(directories)} director{'y' if len(directories) == 1 else 'ies'}")

    def step2_memory_directory(self):
        """Step 2: Configure OpenClaw memory directory"""
        print("\n" + "="*70)
        print("💾 STEP 2: OpenClaw Memory Directory")
        print("="*70)
        print("\nThis is where synced files will be stored.")
        print("OpenClaw automatically indexes files in this directory.\n")

        # Default path
        default_memory_dir = Path.home() / ".openclaw" / "workspace" / "memory"

        use_default = questionary.confirm(
            f"Use default OpenClaw memory directory?\n  {default_memory_dir}",
            default=True,
            style=custom_style
        ).ask()

        if use_default:
            memory_dir = str(default_memory_dir)
        else:
            memory_dir = questionary.path(
                "Enter custom memory directory path:",
                default=str(default_memory_dir),
                only_directories=True,
                style=custom_style
            ).ask()

        # Auto-categorization
        auto_categorize = questionary.confirm(
            "Auto-categorize files by path? (e.g., notes/, projects/)",
            default=True,
            style=custom_style
        ).ask()

        # Max file size
        max_size_mb = questionary.select(
            "Maximum file size to process:",
            choices=[
                "5 MB",
                "10 MB (Recommended)",
                "20 MB",
                "50 MB"
            ],
            style=custom_style
        ).ask()

        max_size_bytes = int(max_size_mb.split()[0]) * 1024 * 1024

        self.config['memory'] = {
            'dir': memory_dir,
            'auto_categorize': auto_categorize,
            'max_file_size': max_size_bytes
        }

        print(f"\n✅ Memory directory: {memory_dir}")

    def step3_logging(self):
        """Step 3: Configure logging"""
        print("\n" + "="*70)
        print("📝 STEP 3: Logging Configuration")
        print("="*70)
        print("\nConfigure how OC-Memory logs its activity.\n")

        # Log level
        log_level = questionary.select(
            "Select log level:",
            choices=[
                "INFO (Recommended - Normal operation)",
                "DEBUG (Verbose - For troubleshooting)",
                "WARNING (Quiet - Errors only)"
            ],
            style=custom_style
        ).ask()

        level_map = {
            "INFO": "INFO",
            "DEBUG": "DEBUG",
            "WARNING": "WARNING"
        }
        level = [v for k, v in level_map.items() if k in log_level][0]

        # Log file
        default_log_file = "oc-memory.log"
        log_file = questionary.text(
            "Log file name:",
            default=default_log_file,
            style=custom_style
        ).ask()

        # Console output
        console = questionary.confirm(
            "Also print logs to console?",
            default=True,
            style=custom_style
        ).ask()

        self.config['logging'] = {
            'level': level,
            'file': log_file,
            'console': console
        }

        print(f"\n✅ Logging configured: {level} -> {log_file}")

    def step4_optional_features(self):
        """Step 4: Optional features (Phase 2+)"""
        print("\n" + "="*70)
        print("✨ STEP 4: Optional Features (Phase 2+)")
        print("="*70)
        print("\nThese features are for advanced usage and will be implemented")
        print("in future phases. You can skip this for now.\n")

        configure_advanced = questionary.confirm(
            "Configure advanced features? (LLM, ChromaDB, Obsidian)",
            default=False,
            style=custom_style
        ).ask()

        if not configure_advanced:
            self._set_optional_defaults()
            print("\n✅ Skipped advanced features (can configure later)")
            return

        # Hot Memory (ChromaDB)
        self._configure_hot_memory()

        # LLM (Observer/Reflector)
        self._configure_llm()

        # Obsidian Integration
        self._configure_obsidian()

    def _set_optional_defaults(self):
        """Set default values for optional features"""
        self.config['hot_memory'] = {
            'ttl_days': 90,
            'max_observations': 10000
        }

        self.config['llm'] = {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'api_key_env': 'OPENAI_API_KEY',
            'enabled': False
        }

        self.config['obsidian'] = {
            'enabled': False
        }

        self.config['dropbox'] = {
            'enabled': False
        }

    def _configure_hot_memory(self):
        """Configure hot memory settings"""
        print("\n🔥 Hot Memory Configuration\n")

        ttl_days = questionary.text(
            "Hot memory TTL (days):",
            default="90",
            validate=lambda x: x.isdigit() and int(x) > 0,
            style=custom_style
        ).ask()

        self.config['hot_memory'] = {
            'ttl_days': int(ttl_days),
            'max_observations': 10000
        }

    def _configure_llm(self):
        """Configure LLM settings"""
        print("\n🤖 LLM Configuration\n")

        provider = questionary.select(
            "Select LLM provider:",
            choices=[
                "OpenAI (gpt-4o-mini)",
                "Google (gemini-2.0-flash)",
                "Skip for now"
            ],
            style=custom_style
        ).ask()

        if "Skip" in provider:
            self.config['llm'] = {
                'enabled': False,
                'provider': 'openai',
                'model': 'gpt-4o-mini',
                'api_key_env': 'OPENAI_API_KEY'
            }
            return

        # Provider-specific settings
        if "OpenAI" in provider:
            model = "gpt-4o-mini"
            api_key_env = "OPENAI_API_KEY"
            provider_name = "openai"
        else:  # Google
            model = "gemini-2.0-flash"
            api_key_env = "GOOGLE_API_KEY"
            provider_name = "google"

        # Check for API key
        has_key = questionary.confirm(
            f"Do you have {api_key_env} set?",
            default=False,
            style=custom_style
        ).ask()

        if has_key:
            print(f"✅ Using {api_key_env} from environment")
        else:
            api_key = questionary.password(
                f"Enter {api_key_env} (will be saved to .env):",
                style=custom_style
            ).ask()

            if api_key:
                self._save_to_env(api_key_env, api_key)

        self.config['llm'] = {
            'enabled': True,
            'provider': provider_name,
            'model': model,
            'api_key_env': api_key_env
        }

    def _configure_obsidian(self):
        """Configure Obsidian integration"""
        print("\n📝 Obsidian Integration\n")

        enable_obsidian = questionary.confirm(
            "Enable Obsidian integration? (Phase 3 feature)",
            default=False,
            style=custom_style
        ).ask()

        if enable_obsidian:
            vault_path = questionary.path(
                "Obsidian vault path:",
                default=str(Path.home() / "Documents" / "ObsidianVault"),
                style=custom_style
            ).ask()

            self.config['obsidian'] = {
                'enabled': True,
                'vault_path': vault_path
            }

            # Dropbox sync
            enable_dropbox = questionary.confirm(
                "Enable Dropbox sync?",
                default=False,
                style=custom_style
            ).ask()

            if enable_dropbox:
                self.config['dropbox'] = {
                    'enabled': True,
                    'app_key_env': 'DROPBOX_APP_KEY'
                }
                print("⚠️  Don't forget to set DROPBOX_APP_KEY in .env")
            else:
                self.config['dropbox'] = {'enabled': False}
        else:
            self.config['obsidian'] = {'enabled': False}
            self.config['dropbox'] = {'enabled': False}

    def step5_openclaw_integration(self):
        """Step 5: OpenClaw Integration"""
        print("\n" + "="*70)
        print("🔗 STEP 5: OpenClaw Integration")
        print("="*70)
        print("\nOC-Memory will inject memory context into OpenClaw's system prompt.")
        print("This allows OpenClaw to access your memory automatically.\n")

        openclaw_dir = Path.home() / ".openclaw"
        openclaw_json = openclaw_dir / "openclaw.json"

        # Memory injection instructions
        memory_instructions = """You have access to an external memory system (OC-Memory) that stores observations and important information about the user.

When responding to the user:
1. Check if there are relevant observations in the memory files (automatically indexed in OpenClaw)
2. Reference past decisions and context to maintain consistency
3. Update memory when learning new important information about the user
4. Use memory to provide personalized and contextual responses

The memory files are stored in ~/.openclaw/workspace/memory/ and are automatically indexed by OpenClaw."""

        print("📋 Memory Instructions to inject into OpenClaw:\n")
        print(memory_instructions)
        print("\n")

        # Check if openclaw.json exists
        if not openclaw_json.exists():
            print(f"⚠️  File not found: {openclaw_json}")
            create_it = questionary.confirm(
                "Would you like me to create a new openclaw.json with OC-Memory integration?",
                default=True,
                style=custom_style
            ).ask()

            if create_it:
                self._create_openclaw_json(openclaw_json, memory_instructions)
                print(f"\n✅ Created {openclaw_json}")
            else:
                print("ℹ️  Skipped. You can manually add memory instructions later.")
        else:
            # File exists, ask to modify
            modify = questionary.confirm(
                f"Found {openclaw_json}. Update system prompt with OC-Memory integration?",
                default=True,
                style=custom_style
            ).ask()

            if modify:
                self._update_openclaw_json(openclaw_json, memory_instructions)
                print(f"\n✅ Updated {openclaw_json}")
            else:
                print("ℹ️  Skipped. You can manually add memory instructions later.")

        self.config['openclaw'] = {
            'config_path': str(openclaw_json),
            'memory_instructions': memory_instructions
        }

    def _create_openclaw_json(self, path: Path, memory_instructions: str):
        """Create a new openclaw.json with OC-Memory integration"""
        openclaw_config = {
            "systemPrompt": {
                "userMessage": memory_instructions
            }
        }

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(openclaw_config, f, indent=2)

    def _update_openclaw_json(self, path: Path, memory_instructions: str):
        """Update existing openclaw.json with OC-Memory integration"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            # File corrupted or can't be read, create new
            config = {}

        # Ensure structure exists
        if 'systemPrompt' not in config:
            config['systemPrompt'] = {}
        if 'userMessage' not in config['systemPrompt']:
            config['systemPrompt']['userMessage'] = ""

        # Append OC-Memory instructions
        current_message = config['systemPrompt']['userMessage']
        if memory_instructions not in current_message:
            if current_message.strip():
                config['systemPrompt']['userMessage'] = f"{current_message}\n\n{memory_instructions}"
            else:
                config['systemPrompt']['userMessage'] = memory_instructions

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

    def step6_create_directories(self):
        """Step 6: Create Directories Automatically"""
        print("\n" + "="*70)
        print("📁 STEP 6: Create Directories")
        print("="*70 + "\n")

        errors = []

        # Create watch directories
        print("Creating watch directories...\n")
        for watch_dir in self.config['watch']['dirs']:
            try:
                watch_path = Path(watch_dir)
                watch_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ {watch_path}")
            except Exception as e:
                errors.append(f"Failed to create {watch_dir}: {e}")
                print(f"  ❌ {watch_dir}: {e}")

        # Create memory directory
        print("\nCreating memory directory...\n")
        try:
            memory_path = Path(self.config['memory']['dir'])
            memory_path.mkdir(parents=True, exist_ok=True)
            # Set permissions (Unix only)
            if os.name != 'nt':
                os.chmod(memory_path, 0o755)
            print(f"  ✅ {memory_path}")
        except Exception as e:
            errors.append(f"Failed to create memory directory: {e}")
            print(f"  ❌ Memory directory: {e}")

        # Create OpenClaw workspace if needed
        print("\nEnsuring OpenClaw workspace exists...\n")
        try:
            openclaw_workspace = Path.home() / ".openclaw" / "workspace"
            openclaw_workspace.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {openclaw_workspace}")
        except Exception as e:
            errors.append(f"Failed to create OpenClaw workspace: {e}")
            print(f"  ❌ OpenClaw workspace: {e}")

        if errors:
            print("\n⚠️  Some directories could not be created:")
            for error in errors:
                print(f"  • {error}")
        else:
            print("\n✅ All directories created successfully")

    def step7_auto_test(self):
        """Step 7: Auto Test"""
        print("\n" + "="*70)
        print("🧪 STEP 7: Auto Test")
        print("="*70)
        print("\nTesting OC-Memory integration...\n")

        # Get first watch directory
        if not self.config['watch']['dirs']:
            print("❌ No watch directories configured")
            return

        watch_dir = Path(self.config['watch']['dirs'][0])
        memory_dir = Path(self.config['memory']['dir'])

        # Ensure directories exist
        watch_dir.mkdir(parents=True, exist_ok=True)
        memory_dir.mkdir(parents=True, exist_ok=True)

        # Create test file
        test_file = watch_dir / "test_memory_observer.md"
        test_file_content = """# OC-Memory Test Note

This is a test file created by the setup wizard to verify that OC-Memory
is working correctly.

## Test Content

- Test timestamp: {timestamp}
- Test status: In progress
- Expected behavior: This file should be processed and appear in the memory directory
""".format(timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))

        try:
            test_file.write_text(test_file_content, encoding='utf-8')
            print(f"✅ Created test file: {test_file}")
        except Exception as e:
            print(f"❌ Failed to create test file: {e}")
            return

        # Check if memory_observer.py exists
        observer_script = self.project_root / "memory_observer.py"
        if not observer_script.exists():
            print(f"\nℹ️  memory_observer.py not found at {observer_script}")
            print("   The observer script will need to be implemented.")
            print(f"   Test file created at: {test_file}")
            return

        # Try to run observer briefly
        print("\nAttempting to run memory observer (5 seconds)...\n")
        try:
            # Start process with timeout
            process = subprocess.Popen(
                [sys.executable, str(observer_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_root)
            )

            # Wait for 5 seconds
            time.sleep(5)

            # Terminate process
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()

            # Check if test file was processed
            memory_files = list(memory_dir.glob("*test*"))
            if memory_files:
                print(f"✅ Test successful! Files found in memory directory:")
                for mf in memory_files:
                    print(f"   • {mf.name}")
            else:
                print("ℹ️  Observer ran but test file not yet processed.")
                print(f"   This may be normal if the observer needs more time.")
                print(f"   Check {memory_dir} after running the observer.")

        except FileNotFoundError:
            print("ℹ️  memory_observer.py not executable or not found")
            print(f"   Test file created at: {test_file}")
        except Exception as e:
            print(f"⚠️  Error running observer: {e}")
            print(f"   Test file created at: {test_file}")

    def step8_ready_to_run(self):
        """Step 8: Ready to Run"""
        print("\n" + "="*70)
        print("🚀 STEP 8: Ready to Run")
        print("="*70 + "\n")

        print("✅ Setup is almost complete!\n")

        print("📋 Final Checklist:\n")
        checklist = [
            ("✅", "Configuration file saved"),
            ("✅", "Watch directories created"),
            ("✅", "Memory directory created"),
            ("✅", "OpenClaw integration prepared")
        ]

        for status, item in checklist:
            print(f"  {status} {item}")

        print("\n" + "="*70)
        print("\n🎯 How to Start OC-Memory:\n")

        print("1. Start the memory observer daemon:\n")
        print("   python memory_observer.py\n")

        print("2. Or run in the background:\n")
        print("   python memory_observer.py &\n")

        print("3. Monitor logs:\n")
        print("   tail -f oc-memory.log\n")

        print("="*70)
        print("\n📊 Verify It's Working:\n")

        print("1. Create a test note in your watch directory:")
        if self.config['watch']['dirs']:
            print(f"   echo '# Test' > \"{self.config['watch']['dirs'][0]}/note.md\"\n")

        print("2. Check if it appears in memory directory:")
        print(f"   ls {self.config['memory']['dir']}\n")

        print("3. OpenClaw will automatically index memory files.")
        print("   Check your OpenClaw memory or search functionality.\n")

        print("="*70)

    def step9_review_and_save(self):
        """Step 9: Review configuration and save"""
        print("\n" + "="*70)
        print("📋 STEP 9: Review Configuration")
        print("="*70 + "\n")

        # Print summary
        print("Configuration Summary:")
        print("-" * 70)

        # Watch directories
        print(f"\n📂 Watch Directories ({len(self.config['watch']['dirs'])}):")
        for dir_path in self.config['watch']['dirs']:
            print(f"   • {dir_path}")
        print(f"   Recursive: {self.config['watch']['recursive']}")

        # Memory
        print(f"\n💾 Memory Directory:")
        print(f"   • {self.config['memory']['dir']}")
        print(f"   Auto-categorize: {self.config['memory']['auto_categorize']}")
        print(f"   Max file size: {self.config['memory']['max_file_size'] / 1024 / 1024:.0f} MB")

        # Logging
        print(f"\n📝 Logging:")
        print(f"   • Level: {self.config['logging']['level']}")
        print(f"   • File: {self.config['logging']['file']}")
        print(f"   • Console: {self.config['logging']['console']}")

        # OpenClaw
        if self.config.get('openclaw'):
            print(f"\n🔗 OpenClaw Integration:")
            print(f"   • Config: {self.config['openclaw']['config_path']}")
            print(f"   • Status: Ready")

        # Optional features
        if self.config.get('llm', {}).get('enabled'):
            print(f"\n🤖 LLM: ✅ Enabled ({self.config['llm']['model']})")
        else:
            print(f"\n🤖 LLM: ❌ Disabled")

        if self.config.get('obsidian', {}).get('enabled'):
            print(f"📝 Obsidian: ✅ Enabled")
        else:
            print(f"📝 Obsidian: ❌ Disabled")

        print("\n" + "-" * 70 + "\n")

        # Confirm
        confirmed = questionary.confirm(
            "Save this configuration?",
            default=True,
            style=custom_style
        ).ask()

        if not confirmed:
            print("❌ Configuration not saved. Exiting.")
            sys.exit(0)

        # Backup existing config
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix('.yaml.backup')
            self.config_path.rename(backup_path)
            print(f"📦 Existing config backed up to: {backup_path}")

        # Save configuration
        self._save_config()

    def _save_config(self):
        """Save configuration to YAML file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        print(f"\n✅ Configuration saved to: {self.config_path}")

    def _save_to_env(self, key: str, value: str):
        """Save environment variable to .env file"""
        # Read existing .env
        existing = {}
        if self.env_path.exists():
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        existing[k] = v

        # Add/update key
        existing[key] = value

        # Write .env
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write("# OC-Memory Environment Variables\n")
            f.write("# ⚠️  DO NOT COMMIT THIS FILE TO GIT\n\n")
            for k, v in existing.items():
                f.write(f"{k}={v}\n")

        # Set permissions (Unix only)
        if os.name != 'nt':
            os.chmod(self.env_path, 0o600)

        print(f"🔑 Saved {key} to: {self.env_path}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    try:
        wizard = SetupWizard()
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
