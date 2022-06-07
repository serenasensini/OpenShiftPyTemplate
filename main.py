from PyInquirer import prompt
from examples import custom_style_2
from prompt_toolkit.validation import Validator, ValidationError
import re
import json

template = {
    "apiVersion": "template.openshift.io/v1",
    "kind": "Template",
    "objects": []
}


class NumberValidator(Validator):

    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(message="Please enter a number.",
                                  cursor_position=len(document.text))


class RFC1123Validator(Validator):

    # def contains_number(self, value):
    #     return any(not c.isdigit() for c in value)

    def contains_symbols(self, value):
        regex = re.compile('^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid name. Only lower case alphanumeric characters, '-' or '.' are allowed.",
                cursor_position=len(document.text))


class PortValidator(Validator):

    def validate(self, document):
        try:
            if 1 <= int(document.text) <= 32768:
                return True
            else:
                raise ValueError
        except ValueError:
            raise ValidationError(message="Please enter a valid port.",
                                  cursor_position=len(document.text))


start = [
    {
        'type': 'confirm',
        'name': 'start_option',
        'message': 'Welcome to simple OpenShift templating. Do you want to start?',
    },
]

template_metadata = [
    {
        'type': 'input',
        'name': 'name',
        'message': 'Let\'s start with the metadata. Choose a name for your template'
    },
    {
        'type': 'input',
        'name': 'openshift.io/display-name',
        'message': 'Display name'
    },
    {
        'type': 'input',
        'name': 'description',
        'message': 'Brief description'
    },
    {
        'type': 'input',
        'name': 'openshift.io/long-description',
        'message': 'Long description'
    },
    {
        'type': 'input',
        'name': 'openshift.io/provider',
        'message': 'Provider'
    },
    {
        'type': 'input',
        'name': 'openshift.io/documentation-url',
        'message': 'Documentation URL'
    },
    {
        'type': 'input',
        'name': 'tags',
        'message': 'Tags (comma-separated values)'
    },
    # {
    #     'type': "input",
    #     "name": "b",
    #     "message": "Enter the second number",
    #     # "validate": NumberValidator,
    #     "filter": lambda val: int(val)
    # }

]

objects = [
    {
        'type': 'list',
        'name': 'resource_select',
        'message': 'Which kind of resource do you want to define?',
        'choices': ["Exit!", "DeploymentConfig", "Deployment", "Service", "ConfigMap", "Secret", "Route"]
    }
]

deploymentconfig_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version?',
        'choices': ["apps.openshift.io/v1", "v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name',
        'validate': RFC1123Validator
    },
    {
        'type': 'input',
        'name': 'replicas',
        'message': 'Number of pod replicas',
        'validate': NumberValidator
    },
    {
        'type': 'input',
        'name': 'image',
        'message': 'Image URL'
    },
    {
        'type': 'input',
        'name': 'image_name',
        'message': 'Image Name'
    },
    {
        'type': 'input',
        'name': 'containerPort',
        'message': 'Port',
        # 'validator': PortValidator
    },
    {
        'type': 'list',
        'name': 'protocol',
        'message': 'Protocol',
        'choices': ["TCP", "UDP"]
    },
    {
        'type': 'input',
        'name': 'selector_value',
        'message': 'Selector value'
    },
]

service_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["v1", "beta"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name'
    },
    {
        'type': 'input',
        'name': 'port',
        'message': 'Container port',
        # 'validator': PortValidator
    },
    {
        'type': 'input',
        'name': 'targetPort',
        'message': 'Target Port',
        # 'validator': PortValidator
    },
    {
        'type': 'list',
        'name': 'protocol',
        'message': 'Protocol',
        'choices': ["TCP", "UDP"]
    },
    {
        'type': 'list',
        'name': 'selector_resource',
        'message': 'Selector resource',
        'choices': ["deploymentconfig", "deployment", "imagestream", "None"]
    },
    {
        'type': 'input',
        'name': 'selector_value',
        'message': 'Selector value'
    },

]

route_select = [
    {
        'type': 'confirm',
        'name': 'service_use',
        'message': 'Do you want to use an existing service?',
    },
]

route_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["route.openshift.io/v1", "v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name'
    },
    {
        'type': 'list',
        'name': 'targetPort',
        'message': 'Target Port',
        'choices': []
    },
    {
        'type': 'list',
        'name': 'serviceName',
        'message': 'Service name',
        'choices': []
    },
    {
        'type': 'confirm',
        'name': 'enable_ssl',
        'message': 'Enable HTTPS using redirect'
    },
]

route_def_w_service = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["route.openshift.io/v1", "v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name'
    },
    {
        'type': 'input',
        'name': 'targetPort',
        'message': 'Target Port',
    },
    {
        'type': 'input',
        'name': 'serviceName',
        'message': 'Service name',
    },
    {
        'type': 'confirm',
        'name': 'enable_ssl',
        'message': 'Enable HTTPS using redirect'
    },
]

secret_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name'
    },
    {
        'type': 'input',
        'name': 'tot_data',
        'message': 'How many entries do you want to configure?',
        # 'validator': NumberValidator
    }
]

secret_data = [
    {
        'type': 'input',
        'name': 'key',
        'message': 'Key'
    },
    {
        'type': 'input',
        'name': 'value',
        'message': 'Value'
    }
]


def general_infos(args):
    metadata = {"metadata": {
        "annotations": {

        },
        "name": ""
    }}

    metadata['metadata']['name'] = args.get("name").lower() if args.get("name") else ''
    metadata['metadata']['annotations']['openshift.io/display-name'] = args.get(
        "openshift.io/display-name") if args.get("openshift.io/display-name") else ''
    metadata['metadata']['annotations']['openshift.io/documentation-url'] = args.get(
        "openshift.io/documentation-url") if args.get("openshift.io/documentation-url") else ''
    metadata['metadata']['annotations']['description'] = args.get(
        "description") if args.get("description") else ''
    metadata['metadata']['annotations']['openshift.io/long-description'] = args.get(
        "openshift.io/long-description") if args.get("openshift.io/long-description") else ''
    metadata['metadata']['annotations']['openshift.io/provider'] = args.get(
        "openshift.io/provider") if args.get("openshift.io/provider") else ''
    metadata['metadata']['annotations']['tags'] = args.get(
        "tags") if args.get("tags") else ''

    return metadata


def object_definition(kind, spec):
    # ONLY FOR DC
    # FIXME: missing env & volumes
    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": kind,
        "metadata": {
            "name": spec.get("name") if spec.get("name") else '',
            "labels":
                {
                    "app": spec.get("selector_value"),
                }
        },

        "spec": {
            "selector": {
                "app": spec.get("selector_value"),
                "deploymentconfig": spec.get("selector_value")
            },
            "replicas": int(spec.get('replicas')) if spec.get('replicas') else 0,
            "strategy": {
                "type": "Rolling",
                "rollingParams": {
                    "updatePeriodSeconds": 1,
                    "intervalSeconds": 1,
                    "timeoutSeconds": 600,
                    "maxUnavailable": "25%",
                    "maxSurge": "25%"
                },
                "resources": {},
                "activeDeadlineSeconds": 1800
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": spec.get("selector_value"),
                        "deploymentconfig": spec.get("selector_value")
                    }
                },
                "spec": {
                    "containers": [],
                    "restartPolicy": "Always",
                    "terminationGracePeriodSeconds": 30,
                    "dnsPolicy": "ClusterFirst",
                    "securityContext": {}
                }
            },
            "triggers": [
                {
                    "type": "ConfigChange"
                }
            ]
        },
    }

    object['spec']['template']['spec']['containers'].append({
        'image': spec.get('image') if spec.get('image') else '',
        'name': spec.get('image_name') if spec.get('image_name') else '',
        'ports': [
            {
                "containerPort": int(spec.get('containerPort')),
                "protocol": spec.get('protocol')
            }
        ] if spec.get('containerPort') else '',
        "imagePullPolicy": "Always",
        "terminationMessagePolicy": "File",
        # "command": [
        #     "/bin/sleep",
        #     "3650d"
        # ],
    })

    template['objects'].append(object)


def service_definition(spec):
    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": "Service",
        "metadata": {
            "name": spec.get("name")
        },
        "spec": {
            "ports": [
                {
                    "name": spec.get("port") + "-" + spec.get("protocol").lower(),
                    "protocol": spec.get("protocol"),
                    "port": int(spec.get("port")),
                    "targetPort": int(spec.get("targetPort"))
                }
            ],
            "selector": {},
            "type": "ClusterIP",
            "sessionAffinity": "None"
        }
    }

    if spec.get("selector_resource") != "None":
        object['spec']['selector'] = {
            spec.get("selector_resource"): spec.get("selector_value")
        }

    template['objects'].append(object)


def route_definition(spec):
    object = {
        "apiVersion": "v1",
        "kind": "Route",
        "metadata": {
            "labels": {},
            "name": spec.get("name")
        },
        "spec": {
            "port": {
                "targetPort": spec.get('targetPort')
            },
            "tls": {

            },
            "to": {
                "kind": "Service",
                "name": spec.get('serviceName'),
                "weight": 100
            },
            "wildcardPolicy": "None"
        }
    }

    if spec.get('enable_ssl'):
        object['spec']['tls'] = {
            "insecureEdgeTerminationPolicy": "Redirect",
            "termination": "edge"
        }
    else:
        del object['spec']['tls']

    template['objects'].append(object)

    # if spec.get("selector_resource") != "None":
    #     object['spec']['selector'] = {
    #         spec.get("selector_resource"): spec.get("selector_value")
    #     }


def secret_definition(apiVersion, name, data):
    object = {
        "apiVersion": apiVersion,
        "stringData": data,
        "kind": "Secret",
        "metadata": {
            "name": name,
        },
        "type": "Opaque"
    }

    template['objects'].append(object)


def get_services():
    services_list = []
    ports_list = []
    template_json = json.dumps(template)
    data = json.loads(template_json)
    for item in data['objects']:
        for key in item:
            if key == 'kind' and item[key] == 'Service':
                ports = item['spec']['ports']
                for port in ports:
                    ports_list.append(port['name'])
                    services_list.append(item['metadata']['name'])
    print(services_list)
    return set(services_list), ports_list


def main():
    # START
    answers = prompt(start, style=custom_style_2)
    if answers.get("start_option"):
        ans_metadata = prompt(template_metadata, style=custom_style_2)
        template.update(general_infos(ans_metadata))

        # DEFINE: objects

        interrupt = True
        while interrupt:
            # which object do you want to create?
            ans_objects_choice = prompt(objects, style=custom_style_2)

            if ans_objects_choice.get("resource_select") == "DeploymentConfig":
                # DEFINE: DC
                ans_container_def = prompt(deploymentconfig_def, style=custom_style_2)
                object_definition('DeploymentConfig', ans_container_def)

            elif ans_objects_choice.get("resource_select") == "Service":
                # DEFINE: service
                ans_service_def = prompt(service_def, style=custom_style_2)
                service_definition(ans_service_def)

            elif ans_objects_choice.get("resource_select") == "Route":

                ans_route_choice = prompt(route_select, style=custom_style_2)
                if ans_route_choice.get('service_use'):
                    # DEFINE: route
                    services_list, ports_list = get_services()
                    if len(services_list) > 0:
                        for item in route_def:
                            if item['name'] == 'serviceName':
                                item['choices'] = services_list
                            elif item['name'] == 'targetPort':
                                item['choices'] = ports_list

                        ans_route_def = prompt(route_def, style=custom_style_2)
                        route_definition(ans_route_def)
                    else:
                        print("No services found in current template. ")

                        ans_route_def = prompt(route_def_w_service, style=custom_style_2)
                        route_definition(ans_route_def)

            elif ans_objects_choice.get("resource_select") == "Deployment":
                print("Not ready yet. Choose another one!")

            elif ans_objects_choice.get("resource_select") == "Secret":

                data = {}
                ans_secret_def = prompt(secret_def, style=custom_style_2)
                count = ans_secret_def.get('tot_data')
                for occurence in range(0, int(count)):
                    ans_secret_data = prompt(secret_data, style=custom_style_2)
                    key = ans_secret_data.get('key')
                    value = ans_secret_data.get('value')
                    data[key] = value
                secret_definition(ans_secret_def.get("apiVersion"), ans_secret_def.get("name"), data)

            elif ans_objects_choice.get("resource_select") == "ConfigMap":
                # FIXME: missing configmap definition
                print("Not ready yet. Choose another one!")

            elif ans_objects_choice.get("resource_select") == "Exit!":
                interrupt = False

        print("Thanks, bye!")
        with open('template.json', 'w+') as f:
            f.write(str(template))
            f.close()


if __name__ == "__main__":
    main()

# # 3rd STEP: objects
#
# objects = []
#
# # DC or D?
#
# name = input("DeploymentConfig or Deployment? ")
#
# # 4th STEP: networking
#
# # 5th STEP: configmaps & secrets
#
# # 6th STEP: params
