from toscaparser.tosca_template import ToscaTemplate
from default import TOSCA_RECIPES_DIR

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

    def execute(self, user):
        for nodetemplate in self.ordered_nodetemplates:
            self.execute_nodetemplate(user, nodetemplate)

        for obj in self.deferred_sync:
            self.log("Saving deferred sync obj %s" % obj)
            obj.no_sync = False
            obj.save()

    def execute_nodetemplate(self, user, nodetemplate):
        if nodetemplate.type not in resources.resources:
            raise Exception("Nodetemplate %s's type %s is not a known resource" % (nodetemplate.name, nodetemplate.type))

        cls = resources.resources[nodetemplate.type]
        #print "work on", cls.__name__, nodetemplate.name
        obj = cls(user, nodetemplate, self)
        obj.create_or_update()
        self.deferred_sync = self.deferred_sync + obj.deferred_sync

    @staticmethod
    def _translate_exception(msg):
        readable = []
        for line in msg.splitlines():
            print line
            if line.strip().startswith('MissingRequiredFieldError'):
                readable.append(line)

        print readable
        return '/n'.join(readable)

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
        # TODO save the models (understand how does XOSResource works)
        except Exception, e:
            # TODO parse only tosca exception
            raise Exception(self._translate_exception(e.message))


