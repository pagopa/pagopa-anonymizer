resource "github_repository" "repository" {
  name        = local.github.repository
  description = "Anonymize text from PII"

  visibility = "public"

  topics = ["pagopa-shared", "pagopa-rtp"]

  has_downloads        = true
  has_issues           = true
  has_projects         = true
  has_wiki             = true
  vulnerability_alerts = true

}