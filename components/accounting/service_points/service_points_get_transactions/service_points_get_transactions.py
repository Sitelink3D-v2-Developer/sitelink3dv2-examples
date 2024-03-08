#!/usr/bin/python
import os
import sys
from tqdm import tqdm

def path_up_to_last(a_last, a_inclusive=True, a_path=os.path.dirname(os.path.realpath(__file__)), a_sep=os.path.sep):
    return a_path[:a_path.rindex(a_sep + a_last + a_sep) + (len(a_sep)+len(a_last) if a_inclusive else 0)]

components_dir = path_up_to_last("components")

sys.path.append(os.path.join(components_dir, "utils"))
from imports import *

for imp in ["args", "utils", "get_token", "rdm_traits", "rdm_list", "rdm_pagination_traits"]:
    exec(import_cmd(components_dir, imp))


session = requests.Session()


def main():
    script_name = os.path.basename(os.path.realpath(__file__))
    
    # >> Argument handling  
    args = handle_arguments(a_description=script_name, a_arg_list=[arg_log_level, arg_datalogger_output_file_name, arg_datalogger_output_folder])
    # << Argument handling

    # >> Server & logging configuration
    url = "https://qa-consumption.topcon.com/transactions/le/{}/stakeholders/{}/consumers/{}".format('3c8b621c-b856-49ba-b6c2-8b3c92455b49','02d01904-81ca-44e0-856a-3c97602adbf3',"a2L1b000000hHTJEA2")
    logging.basicConfig(format=args.log_format, level=int(args.log_level))
    #logging.info("Running {0} for server={1} dc={2} site={3}".format(script_name, server, args.dc, args.site_id))
    # << Server & logging configuration

    # >> Authorization
    headers = {
        #'Authorization': "Bearer S39Ihx_zJ7IApc3ZDDmCFYj-KYXI9xHotpeR-iXv87-Wmh_m4oLbwWotm9c0jZILv3RG6WxgdfljqVAaBWk4iYPvf2EFHe4r_hNfoZfHw_xhGg6zCjw-7X7GfjFg1sJdLSV6z6vOYKlGfXd-k6HB-K7OaWx4kdsaAVUQi0wY2gKShB7LbsV5Oa2X6sPvHxGsEDu8dKng1WtX2PAKpsd4K0PAL9TtiNBXj_qj1BGdbF2eUeT9vAw6xMFaTHCNd",
        'X-Topcon-Auth': "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiI5ODJiNDg0ZC02MzU2LTQ4MjgtODc5Yi01MDdjYzdjNjA1YjUiLCJzdWIiOiJ1cm46WC1Ub3Bjb24iLCJzY3AiOiIqIiwiYWN0Ijp7ImFjY291bnRpbmciOlsiKiJdfSwiZXhwIjoxNzEyMzA0MDAwfQ.RtpjhlBbCzjhicNZbLK3csPAkJs15O3jZWy3hqhWmm4nTQliIOOYCaQBWNMZTXpDLenyigHEAAjJUTIQ8d3dmdshkLjiZ991V61FSpznbNUEpKkXSe3x8CrNLE91FzQ43qbJR_DnijkORLYgBN_yQb0GXGV6H7PvX51ABmjYvMfeV4waCc6zTkEcJiHHcWcqVJEn-qCgoK1VS_ZVExCq3vmbKhCIj_czpGAnus5XC3aC72V3kSZKYPIaUwsU5SWpMexfPCgKux0PgqqG7tv5pfDy0vJ4xGyxwtYwOkQyEUoWVl-tj-HWzcws8nwMrpef9NnVQggiOPurjT7uMj4BQA",
        #'X-Client-Id': "2e020d55e1b4f1868e1b1496d3c923d170f3dcd0ce1e55352c302273ca635fe7d84362442b46f8a567044bd5515510b738a7c608e1b1bedbc247cc475add093e"
    }
    # << Authorization
    logging.info("url:{}".format(url))
    logging.info("headers:{}".format(json.dumps(headers,indent=4)))
    response = session.get(url, headers=headers)
    #response.raise_for_status()
    rj = response.json()

    logging.info(json.dumps(rj, indent=4))

    os.makedirs(args.datalogger_output_folder, exist_ok=True)
    report_file_name = os.path.join(args.datalogger_output_folder, args.datalogger_output_file_name)
    report_file = open(report_file_name, "w")
    report_file.write("Date, Time, Group, Ledger, Item, Product ID, Machine UUID, Units, Price\n")

    # headers = {
    #     'X-Topcon-Auth': "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5MTM4NjI1NS00ZDNmLTQ2YzUtYTc3MS1jZWViMWEwOTdhZGUiLCJzdWIiOiJ1cm46WC1Ub3Bjb24iLCJzY3AiOiIqIiwiYWN0Ijp7IioiOlsiKiJdfSwiZXhwIjoxNzE0MjgyNDMzfQ.dEVaQEXbFHoNsNV7iyBvkmhjEEbtDJqriMCtXrgJYtwuWjGjFQzzJW-ARLNhTxVzC_T0YI6in8SOCY8pefx1smjI8rZZiyLRNIq-31Ha7J1N0YwBdyBEOLO07-0h003vBfw2aHP30zdXxOtnSZKgtXXLo2sr03p6LT7Td_jKD1OmO4Md9AtSFWPacWDn5dUgKsMHEp8o9i4m1A6XhsDYsSuqEM_yBNNBVYr-p1n4st2zErNQ2HIdjEJ0Lq36oDUy6Ce-Qbdu7Do0pV5l9_dwW_6Z_O6vP_X_LdkrY9mP5HRYjpIiFA7ePA4_5FKdmujyMCp8lrfRf8svN9zg1rEZCg"
    # }
    for i, transaction in enumerate(rj["transactions"]):

        transaction_url = "https://qa-consumption.topcon.com/transactions/{}.jsonl".format(transaction["transactionId"])

        response = session.get(transaction_url, headers=headers)
        response.raise_for_status()
        rt = response.text


        for line in response.iter_lines():

            line_json = json.loads(line)
            logging.info(json.dumps(line_json, indent=4))

            service_tag = "-"
            machine_uuid = "-"
            if "extra" in line_json:
                if "service_tag" in line_json["extra"]:
                    service_tag = line_json["extra"]["service_tag"]
                if "machine.uuid" in line_json["extra"]:
                    machine_uuid = line_json["extra"]["machine.uuid"]
            logging.info("MACHEEEEEEEEEEEEEN {}".format(machine_uuid))
            report_file.write("{},{},{},{},{},{},{},{},{}\n".format(line_json["date"], line_json["timestamp"], line_json["group"],line_json["ledger"], line_json["item"], line_json["productID"], machine_uuid, line_json["units"], line_json["price"]))


        # rj = response.json()
        # logging.info(json.dumps(rj,indent=4))
        # for line in response.iter_lines():
        #     if line: 
        #         logging.info(line)
        #         rj = json.loads(line)
        #         #logging.info(json.dumps(rt,indent=4))
        #         service_tag = "-"
        #         if "extra" in rj:
        #             if "service_tag" in rj["extra"]:
        #                 service_tag = rj["extra"]["service_tag"]
        #         report_file.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(transaction["date"],transaction["type"],transaction["clientName"], transaction["id"], transaction["summary"], rj["productID"], rj["subject"], rj["group"], service_tag, rj["units"], rj["price"]))



# {
#     "productID": "7a93b439-7264-4fcb-b8b7-78460ce0e728",
#     "leID": "3c8b621c-b856-49ba-b6c2-8b3c92455b49",
#     "stakeholderID": "c692b473-370c-4c61-af5b-4352e285ae96",
#     "consumerID": "a2L1300000DIpluEAD",
#     "timestamp": "2024-02-08T09:00:42Z",
#     "date": "2024-02-08",
#     "ledger": "Support Desk",
#     "subject": "connection_connected",
#     "item": "Support Client",
#     "detail": "c79f22dd-3689-4b7a-b5f8-dd48b24a1fde",
#     "extra": {
#         "_augmented": {
#             "trapi_dealer": {
#                 "isDealer": false
#             }
#         },
#         "service_tag": "CATD6T"
#     },
#     "group": "Remote Support",
#     "units": 1,
#     "price": 2.00
# }

#         {
#         "id": "a534v000002dTtaAAE",
#         "summary": "Daily summary for 2024-01-25",
#         "secondaryClientName": "Support Desk",
#         "secondaryClientId": "a1n4v000005NJMnAAO",
#         "type": "DEBIT",
#         "teamId": "a2L1300000DIpluEAD",
#         "serialNumberId": null,
#         "externalRefURI": "https://consumption.topcon.com/transactions/838445c4-ea41-4056-80f6-7944e7a0b6d4.jsonl",
#         "date": "2024-01-25T00:00:00.000Z",
#         "createdDate": "2024-01-26T12:31:52.000Z",
#         "clientName": "Support Desk",
#         "amount": 2.0
#     },

if __name__ == "__main__":
    main()    

