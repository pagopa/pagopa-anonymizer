import http from 'k6/http';

export function anonymizePII(anonymizeUri, subKey, inputText) {
    const formData = {
        text: inputText
      };

      let headers = { 
        'Ocp-Apim-Subscription-Key': subKey,
        "Content-Type": "application/json"
    };

    return http.post(anonymizeUri, JSON.stringify(formData), {headers, responseType: "text"});
}