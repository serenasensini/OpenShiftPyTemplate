from PyInquirer import prompt
from examples import custom_style_2
from prompt_toolkit.validation import Validator, ValidationError
import re

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
            raise ValidationError(message="Please enter a number",
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


start = [
    {
        'type': 'confirm',
        'name': 'user_option',
        'message': 'Welcome to simple OpenShift templating. Do you want to start?',
    },
]

metadata = [
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
        'name': 'deployment_choose',
        'message': 'Which kind of resource do you want to define?',
        'choices': ["DeploymentConfig", "Deployment"]
    }
]

deployment_config_spec = [
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
        'message': 'Port'
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

service_choice = [
    {
        'type': 'confirm',
        'name': 'service_choice',
        'message': 'Do you want to define a Service?'
    }
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
        'message': 'Container port'
    },
    {
        'type': 'input',
        'name': 'targetPort',
        'message': 'Target Port'
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
        'choices': ["deploymentconfig", "deployment", "imagestream"]
    },
    {
        'type': 'input',
        'name': 'selector_value',
        'message': 'Selector value'
    },

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

    print(object)
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
            "selector": {
                spec.get("selector_resource"): spec.get("selector_value")
            },
            "type": "ClusterIP",
            "sessionAffinity": "None"
        }
    }

    print(object)
    template['objects'].append(object)


def main():
    answers = prompt(start, style=custom_style_2)
    if answers.get("user_option"):
        ans_metadata = prompt(metadata, style=custom_style_2)
        template.update(general_infos(ans_metadata))

        # objects

        ans_objects_choice = prompt(objects, style=custom_style_2)
        if ans_objects_choice.get("deployment_choose") == "DeploymentConfig":
            # metadata
            ans_container_def = prompt(deployment_config_spec, style=custom_style_2)
            object_definition('DeploymentConfig', ans_container_def)

        ans_service_choice = prompt(service_choice, style=custom_style_2)
        if ans_service_choice.get('service_choice'):
            ans_service_def = prompt(service_def, style=custom_style_2)
            service_definition(ans_service_def)
        # FIXME: missing route definition
        # FIXME: missing configmap definition
        # FIXME: missing secret definition

    print("Final result:")
    print(template)
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
