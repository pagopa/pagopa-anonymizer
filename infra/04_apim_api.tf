###############
##  API Anonymizer  ##
###############
locals {
  apim_anonymizer_api = {
    display_name          = "PagoPA Anonymizer"
    description           = "Microservice to anonymize PII"
    path                  = "anonymizer"
    subscription_required = true
    service_url           = null
  }
}

#######################
##  API Anonymizer ##
#######################
resource "azurerm_api_management_api_version_set" "api_anonymizer_api" {
  name                = "${var.env_short}-anonymizer-api"
  resource_group_name = local.apim.rg
  api_management_name = local.apim.name
  display_name        = local.apim_anonymizer_api.display_name
  versioning_scheme   = "Segment"
}

module "apim_api_anonymizer_api_v1" {
  source = "./.terraform/modules/__v3__/api_management_api"

  name                  = "${local.project}-anonymizer-api"
  api_management_name   = local.apim.name
  resource_group_name   = local.apim.rg
  product_ids           = [local.apim.product_id]
  subscription_required = local.apim_anonymizer_api.subscription_required
  version_set_id        = azurerm_api_management_api_version_set.api_anonymizer_api.id
  api_version           = "v1"

  description  = local.apim_anonymizer_api.description
  display_name = local.apim_anonymizer_api.display_name
  path         = local.apim_anonymizer_api.path
  protocols    = ["https"]
  service_url  = local.apim_anonymizer_api.service_url

  content_format = "openapi"
  content_value  = templatefile("./api/v1/openapi.json", {
    host = local.apim_hostname
  })

  xml_content = templatefile("./policy/v1/_base_policy.xml.tpl", {
    hostname = local.hostname
  })
}