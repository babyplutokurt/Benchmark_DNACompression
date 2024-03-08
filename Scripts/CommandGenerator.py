import json
import os


class CommandGenerator:
    def __init__(self):
        self.config = None
        self.command = None

    def load_config(self, config_path):
        with open(config_path) as json_file:
            self.config = json.load(json_file)

    def generate_command(self):
        raise NotImplementedError("This method should be implemented by subclasses.")


class SZ3CommandGenerator(CommandGenerator):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.executable_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                            'ExternalDependencies',
                                            'SZ3', 'bin', 'sz3')
        self.command = [self.executable_path]
        self.load_config(self.config_path)

    def generate_command(self):
        commands = []
        if not self.config:
            self.load_config(self.config_path)

        # General options
        if self.config['general'].get('help', False):
            self.command.append("-h")
        if self.config['general'].get('SZ2_style_command_line', False):
            self.command.append("-h2")
        if self.config['general'].get('Version', False):
            self.command.append("-v")
        if self.config['general'].get('print_compression_results', False):
            self.command.append("-a")

        # Input/output
        input_file = self.config['input_output'].get('input_file')
        if input_file:
            self.command.extend(["-i", input_file])
        output_file = self.config['input_output'].get('output_file')
        if output_file:
            self.command.extend(["-o", output_file])
        compressed_file = self.config['input_output'].get('compressed_file')
        if compressed_file:
            self.command.extend(["-z", compressed_file])
        if self.config['input_output'].get('output_format', False):
            self.command.append("-t")

        # Data type
        data_type = self.config['data_type'].get('type')
        if data_type == "float":
            self.command.append("-f")
        elif data_type == "double":
            self.command.append("-d")
        elif data_type == "integer":
            integer_width = str(self.config['data_type'].get('integer_width'))
            self.command.extend(["-I", integer_width])

        # Configuration file
        if self.config['configuration_file'].get('use_configuration', False):
            config_file = self.config['configuration_file'].get('file_path')
            self.command.extend(["-c", config_file])

        # Error control
        mode = self.config['error_control'].get('mode')
        if mode:
            self.command.extend(["-M", mode])
            # Add specific error bounds directly after the mode if they are not zero
            error_bounds_keys = ['absolute_error_bound', 'relative_error_bound', 'PSNR', 'normErr']
            for key in error_bounds_keys:
                value = self.config['error_control'].get(key)
                if value:
                    self.command.append(str(value))

        # Dimensions
        dims = self.config['dimensions'].get('dimensionality')
        if dims > 0:
            self.command.append(f"-{dims}")
            for dim in ['nx', 'ny', 'nz', 'np']:
                dim_value = self.config['dimensions'].get(dim)
                if dim_value > 0:
                    self.command.append(str(dim_value))

        commands.append(" ".join(self.command))
        return commands


class FQZCompCommandGenerator_2(CommandGenerator):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.executable_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                            'ExternalDependencies',
                                            'fqzcomp', 'fqzcomp')
        self.load_config(self.config_path)

    def generate_command(self):
        if not self.config:
            self.load_config(self.config_path)

        # Initialize commands list to hold both compression and decompression commands
        commands = []

        # Handle Compression
        compression_options = self.config.get('Compression', {})
        compression_command = [self.executable_path]
        for key, value in compression_options.items():
            if key in ['Q', 's', 'q', 'n'] and value is not None:
                compression_command.extend([f"-{key}", str(value)])
            elif key in ['b', 'e', 'P', 'X', 'S', 'I'] and value:
                compression_command.append(f"-{key}")
        if 'input_file' in compression_options and 'output_file' in compression_options:
            compression_command.append(compression_options['input_file'])
            compression_command.append(compression_options['output_file'])
        commands.append(" ".join(compression_command))

        # Handle Decompression
        decompression_options = self.config.get('Decompression', {})
        if decompression_options:  # Check if decompression section exists
            decompression_command = [self.executable_path, "-d"]
            if 'input_file' in decompression_options:
                decompression_command.append(decompression_options['input_file'])
            if 'output_file' in decompression_options:
                decompression_command.extend(['>', decompression_options['output_file']])
            commands.append(" ".join(decompression_command))

        return commands



class FQZCompCommandGenerator(CommandGenerator):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.executable_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                            'ExternalDependencies',
                                            'fqzcomp', 'fqzcomp')
        self.command = [self.executable_path]
        self.load_config(self.config_path)

    def generate_command(self):
        commands = []
        if not self.config:
            self.load_config(self.config_path)

        # Now, dynamically build the command based on the loaded config
        options = self.config.get('options_compression', {})

        # Example for handling a few options
        quality = options.get('Q')
        if quality:
            self.command.extend(["-Q", str(quality)])

        sequence_level = options.get('s')
        if sequence_level:
            self.command.extend(["-s", str(sequence_level)])
        if options.get('b', False):
            self.command.append("-b")
        if options.get('e', False):
            self.command.append("-e")
        # Continue for other options...

        input_file = self.config.get('input_file')
        if input_file:
            self.command.append(input_file)

        output_file = self.config.get('output_file')
        if output_file:
            self.command.append(output_file)

        commands.append(" ".join(self.command))
        return commands


def generate_sz3_command(config_name='sz3.json'):
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs', config_name)
    generator = SZ3CommandGenerator(config_path)
    return generator.generate_command()


def generate_fqzcomp_command(config_name='fqzcomp.json'):
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs', config_name)
    generator = FQZCompCommandGenerator(config_path)
    return generator.generate_command()

def generate_fqzcomp_command_CompressDecompress(config_name='fqzcomp_2.json'):
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs', config_name)
    generator = FQZCompCommandGenerator_2(config_path)
    return generator.generate_command()


if __name__ == "__main__":
    # Example usage: print the command for sz3 or fqzcomp based on a simple condition or input
    # This is just a placeholder for whatever logic you'd want to use to choose between sz3 and fqzcomp
    tool_name = input("Enter the tool name (sz3 or fqzcomp): ")
    if tool_name.lower() == 'sz3':
        print(generate_sz3_command())
    elif tool_name.lower() == 'fqzcomp':
        print(generate_fqzcomp_command_CompressDecompress())
    else:
        print("Unsupported tool specified.")
