prefix    = "pagopa"
env       = "prod"
env_short = "p"
domain    = "shared"

location_short = "weu"

tags = {
  CreatedBy   = "Terraform"
  Environment = "Prod"
  Owner       = "pagoPA"
  Source      = "https://github.com/pagopa/pagopa-anonymizer"
  CostCenter  = "TS310 - PAGAMENTI & SERVIZI"
}

apim_dns_zone_prefix = "platform"
external_domain      = "pagopa.it"
hostname             = "weuprod.shared.internal.platform.pagopa.it"
