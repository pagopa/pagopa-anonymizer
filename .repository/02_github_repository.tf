
# terraform import github_repository.repository pagopa-anonymizer

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

  delete_branch_on_merge = true

}