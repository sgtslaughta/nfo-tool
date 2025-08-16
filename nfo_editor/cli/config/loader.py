"""
Configuration Loader

Handles YAML configuration file discovery, loading, and validation using
Pydantic schemas. Provides comprehensive error handling and environment
variable override support.

Author: NFO Editor Team
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import os
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .schemas import NFOEditorConfig, ProfileConfig
from pydantic import ValidationError

console = Console()


class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigLoader:
    """
    Configuration file loader and manager.
    
    Handles discovery of configuration files in standard locations,
    loading and validation using Pydantic schemas, and environment
    variable overrides.
    """
    
    def __init__(self, custom_paths: Optional[List[Path]] = None):
        """
        Initialize the configuration loader.
        
        Args:
            custom_paths: Optional list of additional paths to search
        """
        self.config_paths = [
            Path.cwd() / "nfo-editor.yaml",
            Path.cwd() / ".nfo-editor.yaml",
            Path.home() / ".nfo-editor.yaml",
            Path.home() / ".config" / "nfo-editor" / "config.yaml",
        ]
        
        if custom_paths:
            self.config_paths.extend(custom_paths)
        
        # Add XDG config directories if available
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config_home:
            self.config_paths.append(Path(xdg_config_home) / "nfo-editor" / "config.yaml")
        
        self._cached_config: Optional[NFOEditorConfig] = None
        self._config_file_used: Optional[Path] = None
    
    def discover_config_file(self, config_path: Optional[Union[str, Path]] = None) -> Optional[Path]:
        """
        Discover configuration file location.
        
        Args:
            config_path: Specific config file path, or None for auto-discovery
            
        Returns:
            Path to configuration file, or None if not found
            
        Raises:
            ConfigError: If specified config file doesn't exist
        """
        if config_path:
            # Use explicitly specified config file
            config_file = Path(config_path).expanduser().resolve()
            if not config_file.exists():
                raise ConfigError(f"Specified configuration file not found: {config_file}")
            return config_file
        
        # Auto-discovery: check standard locations
        for path in self.config_paths:
            expanded_path = path.expanduser().resolve()
            if expanded_path.exists() and expanded_path.is_file():
                return expanded_path
        
        return None
    
    def load_yaml_file(self, config_file: Path) -> Dict[str, Any]:
        """
        Load YAML configuration file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            Parsed YAML data as dictionary
            
        Raises:
            ConfigError: If file cannot be read or parsed
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return {}
            
            data = yaml.safe_load(content)
            if data is None:
                return {}
                
            if not isinstance(data, dict):
                raise ConfigError(f"Configuration file must contain a YAML object/dictionary, got {type(data).__name__}")
            
            return data
            
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML syntax in {config_file}: {e}")
        except (IOError, OSError) as e:
            raise ConfigError(f"Cannot read configuration file {config_file}: {e}")
    
    def apply_env_overrides(self, config_data: Dict[str, Any], env_prefix: str = "NFO_EDITOR_") -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.
        
        Args:
            config_data: Configuration dictionary to modify
            env_prefix: Prefix for environment variables
            
        Returns:
            Configuration dictionary with overrides applied
        """
        config_data = config_data.copy()
        
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # Convert NFO_EDITOR_RICH_THEME to ["rich", "theme"]
                config_key = key[len(env_prefix):].lower()
                key_parts = config_key.split('_')
                
                # Convert boolean-like strings
                if value.lower() in ('true', '1', 'yes', 'on'):
                    value = True
                elif value.lower() in ('false', '0', 'no', 'off'):
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif '.' in value and value.replace('.', '').isdigit():
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # Keep as string
                
                # Apply nested configuration
                current_dict = config_data
                for i, part in enumerate(key_parts[:-1]):
                    if part not in current_dict:
                        current_dict[part] = {}
                    elif not isinstance(current_dict[part], dict):
                        # Skip if intermediate key is not a dict
                        break
                    current_dict = current_dict[part]
                else:
                    # Set the final key
                    current_dict[key_parts[-1]] = value
        
        return config_data
    
    def validate_config(self, config_data: Dict[str, Any]) -> NFOEditorConfig:
        """
        Validate configuration data using Pydantic schema.
        
        Args:
            config_data: Raw configuration dictionary
            
        Returns:
            Validated NFOEditorConfig instance
            
        Raises:
            ConfigError: If validation fails
        """
        try:
            return NFOEditorConfig(**config_data)
        except ValidationError as e:
            # Format validation errors nicely
            error_messages = []
            for error in e.errors():
                field_path = " -> ".join(str(x) for x in error['loc']) if error['loc'] else 'root'
                error_messages.append(f"  {field_path}: {error['msg']}")
            
            raise ConfigError(
                f"Configuration validation failed:\n" + "\n".join(error_messages) +
                f"\n\nRefer to configuration documentation for valid options."
            )
    
    def load_config(self, config_path: Optional[Union[str, Path]] = None, 
                   validate: bool = True) -> NFOEditorConfig:
        """
        Load and validate configuration from file or defaults.
        
        Args:
            config_path: Specific config file path, or None for auto-discovery
            validate: Whether to validate the configuration
            
        Returns:
            Loaded and validated configuration
            
        Raises:
            ConfigError: If configuration cannot be loaded or is invalid
        """
        # Check cache first
        if self._cached_config is not None and config_path == self._config_file_used:
            return self._cached_config
        
        # Discover config file
        config_file = self.discover_config_file(config_path)
        
        if config_file:
            # Load from file
            config_data = self.load_yaml_file(config_file)
            console.print(f"[dim]Loaded configuration from: {config_file}[/dim]")
        else:
            # Use defaults
            config_data = {}
            if not config_path:  # Only show message for auto-discovery
                console.print("[dim]No configuration file found, using defaults[/dim]")
        
        # Apply environment variable overrides
        env_prefix = config_data.get('env_prefix', 'NFO_EDITOR_')
        config_data = self.apply_env_overrides(config_data, env_prefix)
        
        # Validate configuration
        if validate:
            config = self.validate_config(config_data)
        else:
            # Create unvalidated config for testing
            config = NFOEditorConfig(**config_data)
        
        # Cache the result
        self._cached_config = config
        self._config_file_used = config_file
        
        return config
    
    def get_profile(self, profile_name: str, config: Optional[NFOEditorConfig] = None) -> ProfileConfig:
        """
        Get a specific profile from configuration.
        
        Args:
            profile_name: Name of the profile to retrieve
            config: Configuration to search in, or None to load default
            
        Returns:
            Profile configuration
            
        Raises:
            ConfigError: If profile not found
        """
        if config is None:
            config = self.load_config()
        
        for profile in config.profiles:
            if profile.name == profile_name:
                return profile
        
        available_profiles = [p.name for p in config.profiles]
        raise ConfigError(
            f"Profile '{profile_name}' not found. Available profiles: {available_profiles}"
        )
    
    def list_profiles(self, config: Optional[NFOEditorConfig] = None) -> List[ProfileConfig]:
        """
        List all available profiles.
        
        Args:
            config: Configuration to search in, or None to load default
            
        Returns:
            List of profile configurations
        """
        if config is None:
            config = self.load_config()
        
        return config.profiles
    
    def validate_config_file(self, config_path: Union[str, Path]) -> bool:
        """
        Validate a configuration file without loading it fully.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.load_config(config_path, validate=True)
            return True
        except ConfigError as e:
            console.print(f"[red]Configuration validation failed:[/red] {e}")
            return False
    
    def show_config_locations(self) -> None:
        """Display all possible configuration file locations."""
        console.print(Panel(
            "\n".join([
                "[bold]Configuration file locations (in order of precedence):[/bold]",
                "",
                *[f"  {i+1}. {path}" for i, path in enumerate(self.config_paths)],
                "",
                "[dim]Use --config <path> to specify a custom location[/dim]"
            ]),
            title="📁 Config Discovery",
            border_style="blue"
        ))
    
    def create_example_config(self, output_path: Optional[Path] = None) -> Path:
        """
        Create an example configuration file.
        
        Args:
            output_path: Where to write the example, or None for default location
            
        Returns:
            Path where the example was written
        """
        if output_path is None:
            output_path = Path.cwd() / "nfo-editor-example.yaml"
        
        # Use the template generator
        from .templates import generate_config_template
        template_content = generate_config_template()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        console.print(f"[green]Example configuration written to:[/green] {output_path}")
        return output_path
    
    def clear_cache(self) -> None:
        """Clear cached configuration."""
        self._cached_config = None
        self._config_file_used = None
