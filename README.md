# Entreprises Et Dirigeants

A repository for managing and organizing information about enterprises and their leaders.

## Features

- Track enterprise details and information
- Manage leadership and organizational structure
- Document key personnel and their roles

## Getting Started

To get started with this project, clone the repository and explore the available resources.

```bash
git clone https://github.com/GrandLay-e/EntreprisesEtDirigeants.git
cd EntreprisesEtDirigeants
```

## API

This project uses the **Sirene API** (French business registry API) to fetch enterprise information. The Sirene database contains official data about French businesses including:
- SIREN numbers (unique 9-digit business identifiers)
- Enterprise names and addresses
- Leadership and organizational details
- Business status and activity informatio
- ... 

The API is accessed through HTTP requests to retrieve accurate and up-to-date business information.

## Usage

To use this application, execute it with one of the following parameters:

### Search by SIREN
```bash
python main.py -s <9-digit number>
# or
python main.py --siren <9-digit number>
```
Search using a valid SIREN number (e.g., 123456789).

### Research Query
```bash
python main.py -r <query>
# or
python main.py --research <query>
```
Perform a research query with the specified text.

### Display Help
```bash
python main.py -h
# or
python main.py --help
```
Display the help message.

## Contributing

Contributions are welcome. Please feel free to submit pull requests or open issues for suggestions and improvements.

## License

This project is open source and available under the MIT License.
