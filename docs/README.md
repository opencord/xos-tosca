# TOSCA Interface

A TOSCA interface is available for configuring and controlling CORD. It is
auto-generated from the set of [models](../xos/README.md) configured into the
POD manifest, and includes both core and service-specific models.

## What is TOSCA?

Topology and Orchestration Specification for Cloud Applications (TOSCA) is an
OASIS standard language to describe a topology of cloud based web services,
their components, relationships, and the processes that manage them. The TOSCA
standard includes specifications to describe processes that create or modify
web services. You can read more about it on the
[OASIS](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca)
website.

CORD extends the TOSCA specification to support custom models for services,
allow operators to manage them with a simple and well-known YAML interface.

## Difference between `xos-tosca` and `*-tosca-loader`

When you deploy CORD using helm charts you'll notice that there are two containers
that contains the name `tosca`. There is quite a big difference between them:

- `xos-tosca` contains the TOSCA engine and parser, and exposes a REST api to let you push TOSCA recipes into XOS
- `*-tosca-loader` is a convenience container that pushes a set of recipes into `xos-tosca` and then exits.

## Internals

The `xos-tosca` container autogenerates the TOSCA interface starting from the
`xproto` definition.  When the `xos-tosca` container starts, it connects to
`xos-core` via the `gRPC` API to fetch all the `xproto` definition of the
onboarded models. This includes both `core` and `service` models.  Then using
the `xos-genx` toolchain, it will generates the corresponding TOSCA
specifications.

For example, the `xproto` definition of a compute node in `XOS` is:

```protobuf
message Node::node_policy (XOSBase) {
     required string name = 1 [max_length = 200, content_type = "stripped", blank = False, help_text = "Name of the Node", null = False, db_index = False];
     required manytoone site_deployment->SiteDeployment:nodes = 2 [db_index = True, null = False, blank = False];
}
```

which is then transformed in the following TOSCA spec:

```yaml
tosca_definitions_version: tosca_simple_yaml_1_0

node_types:

    tosca.nodes.Node:
        derived_from: tosca.nodes.Root
        description: "An XOS Node"
        capabilities:
            node:
                type: tosca.capabilities.xos.Node
        properties:
            must-exist:
                type: boolean
                default: false
                description: Allow to reference existing models in TOSCA recipes
            name:
                type: string
                required: false
                description: "Name of the Node"


    tosca.relationships.BelongsToOne:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.SiteDeployment ]


    tosca.capabilities.xos.Node:
        derived_from: tosca.capabilities.Root
        description: Node
```

In TOSCA terminology, the above woule be called a `TOSCA node type`
(although confusingly, it's defined for the `Node` model in CORD,
which represents a server).

## Using TOSCA

Once CORD is up and running, a `node` can be added to a POD
using the TOSCA interface by uploading the following recipe:

```yaml
tosca_definitions_version: tosca_simple_yaml_1_0

description: Load a compute node in XOS

imports:
   - custom_types/node.yaml

topology_template:
  node_templates:

    # A compute node
    GratefulVest:
      type: tosca.nodes.Node
      properties:
        name: Grateful Vest
```

In TOSCA terminology, the above would be called a `TOSCA node template`.

### Where to find the generated specs?

On any running CORD POD, the TOSCA apis are accessible as:

```shell
curl http://<head-node-ip>:<head-node-port>/xos-tosca | python -m json.tool
```

And it will return a list of all the recipes with the related url:

```json
{
  "image": "/custom_type/image",
  "site": "/custom_type/site",
  ...
}
```

For examples, to site the TOSCA spec of the Site model, you can use the URL:

```shell
curl http://<head-node-ip>:<head-node-port>/xos-tosca/custom_type/site
```

If you have a running `xos-tosca` container you can also find generated copies
of the specs in `/opt/xos-tosca/src/tosca/custom_types`.

### How to load a TOSCA recipe in the system

The `xos-tosca` container exposes two endpoint:

```shell
POST http://<cluster-ip>:<tosca-port>/run
POST http://<cluster-ip>:<tosca-port>/delete
```

To load a recipe via `curl` you can use this command:

```shell
curl -H "xos-username: xosadmin@opencord.org" -H "xos-password: <xos-password>" -X POST --data-binary @<path/to/file> http://<cluster-ip>:<tosca-port>/run
```

_If you installed the `xos-core` charts without modifications, the `tosca-port` is `30007`

