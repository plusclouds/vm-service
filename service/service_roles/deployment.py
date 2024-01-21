service_roles = None

def run_service_roles(metadata):
    if "serviceRoles" in metadata.keys():
        logger.info(" ------  Service Roles Check  ------")

        if len(metadata["data"]["serviceRoles"]["data"]) > 0:
            for i in metadata["data"]["serviceRoles"]["data"]:
                logger.info(
                    'Installing unzipping and executing the ' + i["name"] + " execution files in url" + i["url"])

                service = PlusCloudsService(i["name"], i["url"],
                                            i["callback_url"]["ansible_url"],
                                            i["callback_url"]["service_url"])
                try:
                    service.run()
                except Exception as e:
                    logger.error(
                        "Exception occured while download and execution of plusclouds role {}, the following error has been caught {}".format(
                            i["name"], e))
                # Check if api has update flag set to true
                if (str(i["has_update"]).lower() == "true"):
                    try:
                        module = "plusclouds"
                        service_messager(service, "Starting to update the {} module".format(module), "starting")
                        update(module)
                        logger.info("Updated {}".format(module))
                        service_messager(service, "Successfully updated the {} module".format(module), "completed")
                    except Exception as e:
                        service_messager(service,
                                         "Failed updating the {} module with following error {}".format(module, e),
                                         "failed")
                        logger.error(
                            "Exception occurred while updating {}, following error has been caught {}".format(module,
                                                                                                              e))
                else:
                    logger.info("Service is not updated as has_update is not set to true")
                    service_messager(service, "Service is not updated as has_update is not set to true", "completed")
