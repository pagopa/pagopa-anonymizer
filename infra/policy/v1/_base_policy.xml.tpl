<policies>
  <inbound>
    <base/>
    <set-backend-service base-url="https://${hostname}/pagopa-anonymizer"/>
  </inbound>
  <outbound>
    <base/>
  </outbound>
  <backend>
    <base/>
  </backend>
  <on-error>
    <base/>
  </on-error>
</policies>