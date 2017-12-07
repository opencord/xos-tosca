# TOSCA Interface

A TOSCA interface is available for configuring and controlling CORD. It is 
auto-generated from the set of [models](../xos/README.md) configured 
into the POD manifest, and includes both core and service-specific models.

>In `CORD-4.0` this `TOSCA` interface is released as an `alpha` feature.

## What is TOSCA?

Topology and Orchestration Specification for Cloud Applications
(TOSCA) is an OASIS standard language to describe a topology of cloud
based web services, their components, relationships, and the processes
that manage them. The TOSCA standard includes specifications to
describe processes that create or modify web services. You can read
more about it on the
[OASIS](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca)
website.

CORD extends the TOSCA specification to support custom models for
services, allow operators to manage them with a simple and well-known
YAML interface.

## Internals

The `xos-tosca` container autogenerates the TOSCA interface starting
from the `xproto` definition.  When the `xos-tosca` container starts,
it connects to `xos-core`
via the `gRPC` API to fetch all the `xproto` definition of the
onboarded models. This includes both `core` and `service` models.
Then using the `xos-genx` toolchain, it will generates the
corresponding TOSCA specifications.

For example, the `xproto` definition of a compute node in `XOS` is:

```
message Node::node_policy (XOSBase) {
     required string name = 1 [max_length = 200, content_type = "stripped", blank = False, help_text = "Name of the Node", null = False, db_index = False];
     required manytoone site_deployment->SiteDeployment:nodes = 2 [db_index = True, null = False, blank = False];
}
```

which is then transformed in the following TOSCA spec:

```
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

```
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
