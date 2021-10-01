# OpenMensa SH

This parser reads the menu from canteens of the Studentenwerk
Schleswig-Holstein and parses them to the OpenMensa format.

## Usage

```sh
./parser.py <town> [mensa] [days]
```

## Deployment

1. Create `.env` file to set host:

   ```env
   HOST=example.com
   ```

2. Run `docker-compose up -d` (currently depends on external Traefik setup)
