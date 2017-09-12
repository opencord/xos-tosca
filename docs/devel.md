# Development

To run a development environment locally, you'll need to have:
- an XOS configuration running in the frontend vm
- source the xos virtual env (from `xos` root: `source scripts/setup_venv.sh`)
- install `xos-tosca` specific dependencies: `pip install -r requirements`
- an entry in the `/etc/hosts` file that point `xos-core.opencord.org` to you local environment

### Run the xos-tosca process

You can run this either from an IDE or:
```bash
python scr/main.py
```

### Sample call

To send an example request to `xos-tosca`:
```bash
curl -X POST --data-binary @test.yaml 127.0.0.1:9200
```

