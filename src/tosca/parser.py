from toscaparser.tosca_template import ToscaTemplate
from default import TOSCA_RECIPES_DIR

class TOSCA_Parser:

    @staticmethod
    def _translate_exception(msg):
        readable = []
        for line in msg.splitlines():
            print line
            if line.strip().startswith('MissingRequiredFieldError'):
                readable.append(line)

        print readable
        return '/n'.join(readable)

    @staticmethod
    def parse(recipe):
        print recipe
        tmp_file_path = TOSCA_RECIPES_DIR + '/tmp.yaml'

        # write the receive recipe in a tmp file
        tmp_file = open(tmp_file_path, 'w')
        tmp_file.write(recipe)
        tmp_file.close()

        try:
            parsed = ToscaTemplate(tmp_file_path)
            return recipe
        except Exception, e:
            raise Exception(TOSCA_Parser._translate_exception(e.message))


