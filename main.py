from PyInquirer import prompt, style_from_dict, Token
from prompt_toolkit.validation import Validator, ValidationError
import re
import json
import yaml
import sys
import os

custom_style_2 = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

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


class StorageSizeValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('[0-9]+(Gi|Mi){1}')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            if not self.contains_symbols(document.text):
                raise ValueError
        except ValueError:
            raise ValidationError(message="Please enter a valid value (i.e.: 10Gi, 100Mi).",
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
        'message': 'Let\'s start with the metadata. Choose a name for your template',
        'default': 'template'
    },
    {
        'type': 'input',
        'name': 'openshift.io/display-name',
        'message': 'Display name',
        'default': 'OTC Template'
    },
    {
        'type': 'input',
        'name': 'description',
        'message': 'Brief description',
        'default': 'Lorem ipsum'
    },
    {
        'type': 'input',
        'name': 'openshift.io/long-description',
        'message': 'Long description',
        'default': 'Lorem ipsum dolor sit amet'
    },
    {
        'type': 'input',
        'name': 'openshift.io/provider',
        'message': 'Provider',
        'default': 'TheRedCode'
    },
    {
        'type': 'input',
        'name': 'openshift.io/documentation-url',
        'message': 'Documentation URL',
        'default': 'https://theredcode.it'
    },
    {
        'type': 'input',
        'name': 'tags',
        'message': 'Tags (comma-separated values)'
    },

]

objects = [
    {
        'type': 'list',
        'name': 'resource_select',
        'message': 'Which kind of resource do you want to define?',
        'choices': ["Exit!", "DeploymentConfig", "Deployment", "Service", "ConfigMap", "Secret", "Route",
                    "PersistentVolumeClaim", "ImageStream", "PersistentVolume", "StatefulSet"]
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
        'message': 'DeploymentConfig Name',
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
        'message': 'Image URL (specify name and tag)'
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
        'validate': PortValidator
    },
    {
        'type': 'list',
        'name': 'protocol',
        'message': 'Protocol',
        'choices': ["TCP", "UDP"]
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
        'message': 'Service Name',
        'validate': RFC1123Validator
    },
    {
        'type': 'input',
        'name': 'port',
        'message': 'Container port',
        'validate': PortValidator
    },
    {
        'type': 'input',
        'name': 'targetPort',
        'message': 'Target Port',
        'validate': PortValidator
    },
    {
        'type': 'list',
        'name': 'protocol',
        'message': 'Protocol',
        'choices': ["TCP", "UDP"]
    },
]

label_choice = [
    {
        'type': 'confirm',
        'name': 'label_choice',
        'message': 'Do you want to add some labels?',
    }
]

label_num = [
    {
        'type': 'input',
        'name': 'tot_data',
        'message': 'How many labels do you want to configure?',
        'validate': NumberValidator
    }
]

label_def = [
    {
        'type': 'input',
        'name': 'key',
        'message': 'Selector key'
    },
    {
        'type': 'input',
        'name': 'value',
        'message': 'Selector value',
    }
]

image_stream_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["image.openshift.io/v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'ImageStream Name'
    },
    {
        'type': 'input',
        'name': 'tag',
        'message': 'Tag'
    },
    {
        'type': 'list',
        'name': 'kind',
        'message': 'Kind',
        'choices': ["DockerImage"]
    },
    {
        'type': 'input',
        'name': 'imageURL',
        'message': 'Image URL'
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
        'message': 'Route Name',
        'validate': RFC1123Validator
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
        'message': 'Route Name'
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
        'message': 'Secret Name',
        'validate': RFC1123Validator
    },
    {
        'type': 'input',
        'name': 'tot_data',
        'message': 'How many entries do you want to configure?',
        'validate': NumberValidator
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

configmap_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'ConfigMap Name',
        'validate': RFC1123Validator
    },
    {
        'type': 'input',
        'name': 'tot_data',
        'message': 'How many entries do you want to configure?',
        'validate': NumberValidator
    }
]

configmap_data = [
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

pvc_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'PVC Name'
    },
    {
        'type': 'list',
        'name': 'storageMode',
        'message': 'Storage Mode',
        'choices': ["ReadOnlyMany", "ReadWriteMany", "ReadWriteOnce"]
    },
    {
        'type': 'input',
        'name': 'storageSize',
        'message': 'Storage size (i.e.: 1Gi, 100Mi)',
        'validate': StorageSizeValidator
    },
    {
        'type': 'input',
        'name': 'storageClass',
        'message': 'StorageClass'
    },
]

pv_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version',
        'choices': ["v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'PV Name'
    },
    {
        'type': 'list',
        'name': 'storageMode',
        'message': 'Storage Mode',
        'choices': ["ReadOnlyMany", "ReadWriteMany", "ReadWriteOnce"]
    },
    {
        'type': 'input',
        'name': 'storageSize',
        'message': 'Storage size (i.e.: 1Gi, 100Mi)',
        'validate': StorageSizeValidator
    },
    {
        'type': 'input',
        'name': 'storageClass',
        'message': 'StorageClass'
    },
    {
        'type': 'list',
        'name': 'persistentVolumeReclaimPolicy',
        'message': 'Reclaim Policy',
        'choices': ["Retain", "Recycle", "Delete"]
    },
]

deployment_def = [
    {
        'type': 'list',
        'name': 'apiVersion',
        'message': 'API Version?',
        'choices': ["apps/v1"]
    },
    {
        'type': 'input',
        'name': 'name',
        'message': 'Deployment Name',
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
        'message': 'Image URL (specify name and tag)'
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
        'validate': PortValidator
    },
    {
        'type': 'list',
        'name': 'protocol',
        'message': 'Protocol',
        'choices': ["TCP", "UDP"]
    },
    {
        'type': 'list',
        'name': 'imagePullPolicy',
        'message': 'Image Pull Policy',
        'choices': ["Always", "IfNotPresent", "Never"]
    },
    {
        'type': 'list',
        'name': 'restartPolicy',
        'message': 'POD Restart Policy',
        'choices': ["Always", "OnFailure", "Never"]
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


def image_stream_definition(spec, labels):
    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": "ImageStream",
        "metadata": {
            "name": spec.get("name")
        },
        "spec": {
            "tags": [
                {
                    "name": spec.get("tag"),
                    "from": {
                        "kind": spec.get("kind"),
                        "name": spec.get("imageURL")
                    },
                    "referencePolicy": {
                        "type": "Source"
                    }
                }
            ]
        }
    }

    template['objects'].append(object)


def dc_definition(spec, labels):
    # ONLY FOR DC
    # FIXME: missing env & volumes
    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": "DeploymentConfig",
        "metadata": {
            "name": spec.get("name") if spec.get("name") else '',
            "labels": labels
        },

        "spec": {
            "selector": {},
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
                        "app": spec.get("selector_value") if not spec.get("selector_value") is None else "",
                        "deploymentconfig": spec.get("selector_value") if not spec.get(
                            "selector_value") is None else "",
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

    if spec.get("selector_value"):
        object['spec'] = {
            "app": spec.get("selector_value") if not spec.get("selector_value") is None else "",
            "deploymentconfig": spec.get("selector_value") if not spec.get("selector_value") is None else ""
        }

    template['objects'].append(object)


def service_definition(spec, labels):
    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": "Service",
        "metadata": {
            "name": spec.get("name"),
            "labels": labels
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
            spec.get("selector_resource"): spec.get("selector_value") if not spec.get("selector_value") is None else "",
        }

    template['objects'].append(object)


def route_definition(spec, labels):
    object = {
        "apiVersion": "v1",
        "kind": "Route",
        "metadata": {
            "labels": labels,
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


def configmap_definition(apiVersion, name, labels, data):
    object = {
        "apiVersion": apiVersion,
        "data": data,
        "kind": "ConfigMap",
        "metadata": {
            "name": name,
            "labels": labels
        },
        "type": "Opaque"
    }

    template['objects'].append(object)


def secret_definition(apiVersion, name, labels, data):
    object = {
        "apiVersion": apiVersion,
        "stringData": data,
        "kind": "Secret",
        "metadata": {
            "name": name,
            "labels": labels
        },
        "type": "Opaque"
    }

    template['objects'].append(object)


def pvc_definition(spec, labels):
    object = {
        "kind": "PersistentVolumeClaim",
        "apiVersion": spec.get("apiVersion"),
        "metadata": {
            "name": spec.get("name"),
            "labels": labels
        },
        "spec": {
            "accessModes": [
                spec.get("storageMode")
            ],
            "resources": {
                "requests": {
                    "storage": spec.get("storageSize")
                }
            },
            "storageClassName": spec.get("storageClass")
        }
    }

    template['objects'].append(object)


def pv_definition(spec, labels):
    object = {
        "kind": "PersistentVolume",
        "apiVersion": spec.get("apiVersion"),
        "metadata": {
            "name": spec.get("name"),
            "labels": labels
        },
        "spec": {
            "accessModes": [
                spec.get("storageMode")
            ],
            "resources": {
                "requests": {
                    "storage": spec.get("storageSize")
                }
            },
            "persistentVolumeReclaimPolicy": spec.get("persistentVolumeReclaimPolicy"),
            "storageClassName": spec.get("storageClass")
        }
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


def deployment_definition(spec, labels):
    object = {
        "apiVersion": spec.get("apiVersion"),
        "kind": "Deployment",
        "metadata": {
            "name": spec.get("name") if spec.get("name") else '',
            "labels": labels
        },

        "spec": {
            "selector": {
                "matchLabels": labels
            },
            "replicas": int(spec.get('replicas')) if spec.get('replicas') else 0,
            "template": {
                "metadata": {
                    "labels": {
                        "app": spec.get("selector_value") if not spec.get("selector_value") is None else "",
                        "deploymentconfig": spec.get("selector_value") if not spec.get(
                            "selector_value") is None else "",
                    }
                },
                "spec": {
                    "containers": [],
                    "restartPolicy": spec.get('restartPolicy'),
                    "terminationGracePeriodSeconds": 30,
                    "dnsPolicy": "ClusterFirst",
                    "securityContext": {}
                }
            }
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
        "imagePullPolicy": spec.get('imagePullPolicy')
    })

    if spec.get("selector_value"):
        object['spec'] = {
            "app": spec.get("selector_value") if not spec.get("selector_value") is None else "",
            "deploymentconfig": spec.get("selector_value") if not spec.get("selector_value") is None else ""
        }

    template['objects'].append(object)


def main():
    print("""
            #################################
              ______   .___________.  ______ 
             /  __  \  |           | /      |
            |  |  |  | `---|  |----`|  ,----'
            |  |  |  |     |  |     |  |     
            |  `--'  |     |  |     |  `----.
             \______/      |__|      \______|
                                             
            #################################
                                                   
            Welcome to OpenShift Template Configurator.
            
            A simple wizard to create a template for 
            OpenShift, based on specs available
            on the documentation.

            #################################
            
            For further information: 
            https://access.redhat.com/documentation/en-us/openshift_container_platform/4.1/html/images/using-templates
    """)
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

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                dc_definition(ans_container_def, labels)

            elif ans_objects_choice.get("resource_select") == "Service":
                # DEFINE: service
                ans_service_def = prompt(service_def, style=custom_style_2)

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                service_definition(ans_service_def, labels)

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

                        labels = {}
                        ans_labels_choice = prompt(label_choice, style=custom_style_2)
                        if ans_labels_choice.get('label_choice'):
                            ans_labels_num = prompt(label_num, style=custom_style_2)
                            count = ans_labels_num.get('tot_data')
                            for occurrence in range(0, int(count)):
                                ans_labels_data = prompt(label_def, style=custom_style_2)
                                key = ans_labels_data.get('key')
                                value = ans_labels_data.get('value')
                                labels[key] = value

                        route_definition(ans_route_def, labels)
                    else:
                        print("No services found in current template. ")

                        ans_route_def = prompt(route_def_w_service, style=custom_style_2)

                        labels = {}
                        ans_labels_choice = prompt(label_choice, style=custom_style_2)
                        if ans_labels_choice.get('label_choice'):
                            ans_labels_num = prompt(label_num, style=custom_style_2)
                            count = ans_labels_num.get('tot_data')
                            for occurrence in range(0, int(count)):
                                ans_labels_data = prompt(label_def, style=custom_style_2)
                                key = ans_labels_data.get('key')
                                value = ans_labels_data.get('value')
                                labels[key] = value

                        route_definition(ans_route_def, labels)

            elif ans_objects_choice.get("resource_select") == "Secret":

                data = {}
                ans_secret_def = prompt(secret_def, style=custom_style_2)
                count = ans_secret_def.get('tot_data')
                for occurrence in range(0, int(count)):
                    ans_secret_data = prompt(secret_data, style=custom_style_2)
                    key = ans_secret_data.get('key')
                    value = ans_secret_data.get('value')
                    data[key] = value

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                secret_definition(ans_secret_def.get("apiVersion"), ans_secret_def.get("name"), labels, data)

            elif ans_objects_choice.get("resource_select") == "ConfigMap":
                data = {}
                ans_configmap_def = prompt(configmap_def, style=custom_style_2)
                count = ans_configmap_def.get('tot_data')
                for occurrence in range(0, int(count)):
                    ans_configmap_data = prompt(configmap_data, style=custom_style_2)
                    key = ans_configmap_data.get('key')
                    value = ans_configmap_data.get('value')
                    data[key] = value

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                configmap_definition(ans_configmap_def.get("apiVersion"), ans_configmap_def.get("name"), labels, data)

            elif ans_objects_choice.get("resource_select") == "PersistentVolumeClaim":
                # DEFINE: PVC
                ans_pvc_choice = prompt(pvc_def, style=custom_style_2)

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                pvc_definition(ans_pvc_choice, labels)

            elif ans_objects_choice.get("resource_select") == "ImageStream":
                # DEFINE: ImageStream
                ans_image_stream_choice = prompt(image_stream_def, style=custom_style_2)

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                image_stream_definition(ans_image_stream_choice, data)

            elif ans_objects_choice.get("resource_select") == "Deployment":
                # DEFINE: DEPLOYMENT
                ans_container_def = prompt(deployment_def, style=custom_style_2)

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                deployment_definition(ans_container_def, labels)

            elif ans_objects_choice.get("resource_select") == "PersistentVolume":
                # DEFINE: PV
                ans_pv_choice = prompt(pv_def, style=custom_style_2)

                labels = {}
                ans_labels_choice = prompt(label_choice, style=custom_style_2)
                if ans_labels_choice.get('label_choice'):
                    ans_labels_num = prompt(label_num, style=custom_style_2)
                    count = ans_labels_num.get('tot_data')
                    for occurrence in range(0, int(count)):
                        ans_labels_data = prompt(label_def, style=custom_style_2)
                        key = ans_labels_data.get('key')
                        value = ans_labels_data.get('value')
                        labels[key] = value

                pv_definition(ans_pv_choice, labels)

            elif ans_objects_choice.get("resource_select") == "StatefulSet":
                print("Not ready yet. Choose another one!")

            elif ans_objects_choice.get("resource_select") == "Exit!":
                interrupt = False

        template_quoted = str(template).replace("\'", "\"")

        with open('template.json', 'w+') as f:
            f.write(str(template_quoted))
            f.close()

        try:
            with open('template.json', 'r') as json_in, open('template.yaml', "w") as yaml_out:
                json_payload = json.load(json_in)
                result = yaml.dump(json_payload, sort_keys=False)
                yaml_out.write(result)
        except Exception as e:
            print("Created template is not valid.")

    print("Thanks, bye!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
