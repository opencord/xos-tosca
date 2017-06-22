from toscaparser.tosca_template import ToscaTemplate
from default import TOSCA_RECIPES_DIR
from resources import RESOURCES
from grpc._channel import _Rendezvous

class TOSCA_Parser:

    def compute_dependencies(self):
        nodetemplates_by_name = {}
        for nodetemplate in self.template.nodetemplates:
            nodetemplates_by_name[nodetemplate.name] = nodetemplate

        self.nodetemplates_by_name = nodetemplates_by_name

        for nodetemplate in self.template.nodetemplates:
            nodetemplate.dependencies = []
            nodetemplate.dependencies_names = []
            for reqs in nodetemplate.requirements:
                for (k,v) in reqs.items():
                    name = v["node"]
                    if (name in nodetemplates_by_name):
                        nodetemplate.dependencies.append(nodetemplates_by_name[name])
                        nodetemplate.dependencies_names.append(name)

                    # go another level deep, as our requirements can have requirements...
                    for sd_req in v.get("requirements",[]):
                        for (sd_req_k, sd_req_v) in sd_req.items():
                            name = sd_req_v["node"]
                            if (name in nodetemplates_by_name):
                                nodetemplate.dependencies.append(nodetemplates_by_name[name])
                                nodetemplate.dependencies_names.append(name)

    def topsort_dependencies(self):
        # stolen from observer
        g = self.nodetemplates_by_name

        # Get set of all nodes, including those without outgoing edges
        keys = set(g.keys())
        values = set({})
        for v in g.values():
            values = values | set(v.dependencies_names)

        all_nodes = list(keys | values)
        steps = all_nodes


        # Final order
        order = []

        # DFS stack, not using recursion
        stack = []

        # Unmarked set
        unmarked = all_nodes

        # visiting = [] - skip, don't expect 1000s of nodes, |E|/|V| is small

        while unmarked:
            stack.insert(0, unmarked[0])  # push first unmarked

            while (stack):
                n = stack[0]
                add = True
                try:
                    for m in g[n].dependencies_names:
                        if (m in unmarked):
                            add = False
                            stack.insert(0, m)
                except KeyError:
                    pass
                if (add):
                    if (n in steps and n not in order):
                        order.append(n)
                    item = stack.pop(0)
                    try:
                        unmarked.remove(item)
                    except ValueError:
                        pass

        noorder = list(set(steps) - set(order))
        return order + noorder

    def execute(self):
        for nodetemplate in self.ordered_nodetemplates:
            self.execute_nodetemplate(nodetemplate)

    def execute_nodetemplate(self, nodetemplate):
        node_class = nodetemplate.type.replace("tosca.nodes.", "")
        if node_class not in RESOURCES:
            raise Exception("Nodetemplate %s's type %s is not a known resource" % (nodetemplate.name, node_class))

        # find the class corresponding to a node
        cls = RESOURCES[node_class]


        # read properties from TOSCA
        data = nodetemplate.templates[nodetemplate.name]['properties']

        TOSCA_Parser.creat_or_update(cls, data)

    @staticmethod
    def populate_model(model, data):
        for k,v in data.iteritems():
            setattr(model, k, v)
        return model

    @staticmethod
    def creat_or_update(cls, data):

        # default case
        if data.get('name'):
            used_key = 'name'
        else:
            used_key = data.keys()[0]

        models = cls.objects.filter(**{used_key: data[used_key]})

        if len(models) == 1:
            print "[XOS-Tosca] Model %s already exist, updating..." % data[used_key]
            model = models[0]
        elif len(models) == 0:
            model = cls.objects.new()
            print "[XOS-Tosca] Model %s is new, creating..." % data[used_key]
        else:
            raise Exception("[XOS-Tosca] Model %s has multiple instances, I can't handle it" % data[used_key])

        model = TOSCA_Parser.populate_model(model, data)
        model.save()


    @staticmethod
    def _translate_exception(msg):
        readable = []
        for line in msg.splitlines():
            print line
            if line.strip().startswith('MissingRequiredFieldError'):
                readable.append(line)

        if len(readable) > 0:
            return '/n'.join(readable)
        else:
            return msg

    def __init__(self, recipe):

        self.template = None
        self.nodetemplates_by_name = None
        self.ordered_nodetemplates = []
        self.ordered_names = None

        tmp_file_path = TOSCA_RECIPES_DIR + '/tmp.yaml'

        # write the receive recipe in a tmp file
        tmp_file = open(tmp_file_path, 'w')
        tmp_file.write(recipe)
        tmp_file.close()

        try:
            self.template = ToscaTemplate(tmp_file_path)
            self.compute_dependencies()
            self.ordered_names = self.topsort_dependencies()
            for name in self.ordered_names:
                if name in self.nodetemplates_by_name:
                    self.ordered_nodetemplates.append(self.nodetemplates_by_name[name])

            self.execute()

        except Exception as e:
            print e
            import sys, os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            raise Exception(self._translate_exception(e.message))


