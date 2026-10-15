import { SharedArray } from 'k6/data';
import exec from 'k6/execution';
import { check } from 'k6';
import { anonymizePII } from './modules/anonymizer_client.js';

export const options = JSON.parse(open(__ENV.TEST_TYPE));

const environments = new SharedArray('environments', function () {
  return JSON.parse(open(`./${__ENV.VARS}`)).environment;
});

export default function () {
  const uniqueId = exec.scenario.iterationInTest.toString(16).padStart(12, '0');
  const references = Array.from(
    { length: 10 }, (_, index) => `riferimento${index}${uniqueId}`
  ).join(' ');
  const response = anonymizePII(
    environments[0].anonymizeUri,
    __ENV.SUBSCRIPTION_KEY,
    `Pagamento per Mario Rossi ${references}`
  );

  check(response, {
    'status is 200': (res) => res.status === 200,
    'person is masked': (res) => {
      if (res.status !== 200) {
        return false;
      }
      const text = res.json('text');
      return typeof text === 'string'
        && text.includes('M**** R****')
        && !text.includes('Mario Rossi');
    }
  });
}
