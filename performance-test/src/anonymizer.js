import { SharedArray } from 'k6/data';
import { check } from 'k6';
import { anonymizePII } from './modules/anonymizer_client.js';

export const options = JSON.parse(open(__ENV.TEST_TYPE));

const varsArray = new SharedArray('vars', function () {
  return JSON.parse(open(`./${__ENV.VARS}`)).environment;
});

const vars = varsArray[0];
const anonymizeUri = `${vars.anonymizeUri}`;
const subKey = `${__ENV.SUBSCRIPTION_KEY}`;

export function setup() {
  // 2. setup code
}

const MIXED_PII_TEXT = "Multa per Mario Rossi il giorno 12/07/2025 alle ore 11:00, codice fiscale GTRQWF12L23B157A e carta identita n. AA00000AA, domiciliato in Piazza San Pietro n. 35. Pagato attraverso iban IT47J0990650025128761820997 per autovettura targata XX000XX. Contatti numero telefonico 3313516333 ed email test@pagopa.it. Per assistenza andare sul sito web www.test.it";
const MIXED_ANONYMIZED_TEXT = "Multa per <PERSON> il giorno <ANONYMIZED> alle ore 11:00, codice fiscale <FISCAL_CODE> e carta identita n. <ANONYMIZED>, domiciliato in <ADDRESS>. Pagato attraverso iban <ANONYMIZED> per autovettura targata <PLATE_NUMBER>. Contatti numero telefonico <PHONE> ed email <EMAIL>. Per assistenza andare sul sito web <ANONYMIZED>";
export default function (data) {
  // 3. VU code
  let response = anonymizePII(anonymizeUri, subKey, MIXED_PII_TEXT);

  console.log("Anonymize call, Status " + response.status);

  check(response, {
    'Anonymize status is 200': (response) => response.status === 200,
    'Anonymize body not null': (response) => response.body !== null && response.body !== undefined,
    'PIIs have been anonymized': (response) => JSON.parse(response.body).text == MIXED_ANONYMIZED_TEXT
  });
}

export function teardown(data) {
  // 4. teardown code
}