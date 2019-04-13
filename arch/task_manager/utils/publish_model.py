#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import grpc
from arch.api.proto import model_service_pb2
from arch.api.proto import model_service_pb2_grpc
from arch.api.utils import dtable_utils
import copy
from arch.task_manager.settings import logger, PARTY_ID


def load_model(config_data):
    for serving in config_data.get('servings'):
        with grpc.insecure_channel(serving) as channel:
            stub = model_service_pb2_grpc.ModelServiceStub(channel)
            load_model_request = model_service_pb2.PublishRequest()
            for role_name, role_party in config_data.get("role").items():
                for _party_id in role_party:
                    load_model_request.role[role_name].partyId.append(_party_id)
            for role_name, role_model_config in config_data.get("model").items():
                for _party_id, role_party_model_config in role_model_config.items():
                    table_config = copy.deepcopy(role_model_config)
                    table_config['scene_id'] = config_data.get('scene_id')
                    table_config['local'] = {'role': role_name, 'party_id': _party_id}
                    table_config['role'] = config_data.get('role')
                    table_config['data_type'] = 'model'
                    table_name, namespace = dtable_utils.get_table_info(config=table_config)
                    load_model_request.model[role_name].roleModelInfo[int(_party_id)].tableName = table_name
                    load_model_request.model[role_name].roleModelInfo[int(_party_id)].namespace = namespace
            for role_name, role_party in config_data.get("role").items():
                for _party_id in role_party:
                    if _party_id == PARTY_ID:
                        load_model_request.local.role = role_name
                        load_model_request.local.partyId = _party_id
                        logger.info(load_model_request)
                        response = stub.publishLoad(load_model_request)
                        logger.info(response)


def publish_online(config_data):
    for serving in config_data.get('servings'):
        with grpc.insecure_channel(serving) as channel:
            stub = model_service_pb2_grpc.ModelServiceStub(channel)
            publish_model_request = model_service_pb2.PublishRequest()
            for role_name, role_party in config_data.get("role").items():
                for _party_id in role_party:
                    publish_model_request.role[role_name].partyId.append(_party_id)

            for role_name, role_model_config in config_data.get("model").items():
                if role_name != config_data.get('local').get('role'):
                    continue
                for _party_id, role_party_model_config in role_model_config.items():
                    table_config = copy.deepcopy(role_model_config)
                    table_config['scene_id'] = config_data.get('scene_id')
                    table_config['local'] = {'role': role_name, 'party_id': _party_id}
                    table_config['role'] = config_data.get('role')
                    table_config['data_type'] = 'model'
                    table_name, namespace = dtable_utils.get_table_info(config=table_config)
                    publish_model_request.model[role_name].roleModelInfo[int(_party_id)].tableName = table_name
                    publish_model_request.model[role_name].roleModelInfo[int(_party_id)].namespace = namespace
            publish_model_request.local.role = config_data.get('local').get('role')
            publish_model_request.local.partyId = config_data.get('local').get('party_id')
            logger.info(publish_model_request)
            response = stub.publishOnline(publish_model_request)
            logger.info(response)
