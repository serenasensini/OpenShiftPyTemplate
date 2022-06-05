from PyInquirer import prompt
from examples import custom_style_2
from prompt_toolkit.validation import Validator, ValidationError

template = {
    "apiVersion": "template.openshift.io/v1",
    "kind": "Template",
    "objects": []
}

# class NumberValidator(Validator):
#
#     def validate(self, document):
#         try:
#             int(document.text)
#         except ValueError:
#             raise ValidationError(message="Please enter a number",
#                                   cursor_position=len(document.text))


start = [
    {
        'type': 'confirm',
        'name': 'user_option',
        'message': 'Welcome to simple OpenShift templating. Do you want to start?',
    },
]

template_name = [
    {
        'type': 'input',
        'name': 'name',
        'message': 'Let\'s start with the metadata. Choose a name for your template'
    }
]

metadata = [
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
        'name': 'openshift.io/provider-display-name',
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
        'choices': ["v1", "beta"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'Name'
    },
    {
        'type': 'input',
        'name': 'replicas',
        'message': 'Number of pod replicas'
    },
    {
        'type': 'input',
        'name': 'image',
        'message': 'Image URL'
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
        'type': 'list',
        'name': 'protocol',
        'message': 'Protocol',
        'choices': ["TCP", "UDP"]
    },
    {
        'type': 'input',
        'name': 'targetPort',
        'message': 'Target Port'
    },
    {
        'type': 'list',
        'name': 'selector_resource',
        'message': 'Selector resource',
        'choices': ["deploymentconfig", "imagestream"]
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

        }
    }}

    metadata['metadata']['annotations']['openshift.io/display-name'] = args.get(
        "openshift.io/display-name") if args.get("openshift.io/display-name") else ''
    metadata['metadata']['annotations']['openshift.io/documentation-url'] = args.get(
        "openshift.io/documentation-url") if args.get("openshift.io/documentation-url") else ''
    metadata['metadata']['annotations']['description'] = args.get(
        "description") if args.get("description") else ''
    metadata['metadata']['annotations']['openshift.io/long-description'] = args.get(
        "openshift.io/long-description") if args.get("openshift.io/long-description") else ''
    metadata['metadata']['annotations']['openshift.io/display-name'] = args.get(
        "openshift.io/provider-display-name") if args.get("openshift.io/provider-display-name") else ''
    metadata['metadata']['annotations']['tags'] = args.get(
        "tags") if args.get("tags") else ''

    return metadata


def object_definition(kind, spec):

    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": kind,
        "metadata": {},
        "spec": {
            "selector": {}
        },
        "template": {
            "spec": {
                "containers": [],
                "restartPolicy": "Always",
                "terminationGracePeriodSeconds": 30,
                "dnsPolicy": "ClusterFirst",
                "securityContext": {}
            }
        }
    }

    object['metadata']['name'] = spec.get(
        "name") if spec.get("name") else ''

    object['spec']['replicas'] = spec.get('replicas') if spec.get('replicas') else ''
    object['spec']['selector']['deploymentconfig'] = spec.get('selector_value')
    object['template']['spec']['containers'].append({
        'image': spec.get('image') if spec.get('image') else '',
        'ports': [
            {
                "containerPort": spec.get('containerPort'),
                "protocol": spec.get('protocol')
            }
        ] if spec.get('containerPort') else '',
        "imagePullPolicy": "Always"
    })

    print(object)
    template['objects'].append(object)


def service_definition(spec):
    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": "Service",
        "metadata": {},
        "spec": {
            "ports": [
                {
                    "name": spec.get("name"),
                    "protocol": spec.get("protocol"),
                    "port": spec.get("port"),
                    "targetPort": spec.get("targetPort")
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
    if answers.get("user_option") :
        ans_template_name = prompt(template_name, style=custom_style_2)
        template.update(ans_template_name)
        ans_metadata = prompt(metadata, style=custom_style_2)
        template.update(general_infos(ans_metadata))

        # objects

        ans_objects_choice = prompt(objects, style=custom_style_2)
        if ans_objects_choice.get("deployment_choose") == "DeploymentConfig":
            # metadata
            ans_container_def = prompt(deployment_config_spec, style=custom_style_2)
            object_definition('DeploymentConfig', ans_container_def)
            # FIXME spec:strategy
            # FIXME spec:selector

        ans_service_choice = prompt(service_choice, style=custom_style_2)
        if ans_service_choice.get('service_choice'):
            ans_service_def = prompt(service_def, style=custom_style_2)
            service_definition(ans_service_def)

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
