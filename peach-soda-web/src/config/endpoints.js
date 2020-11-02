const baseUrl = 'http://2m8qpxhytd.execute-api.us-east-2.amazonaws.com/dev'

export function getSuggestionsEndpoint() {
    return baseUrl + '/suggestions'
};

export function postSuggestionEndpoint() {
    return baseUrl + '/suggestions'
}

export function getASuggestionEndpoint(suggestion_id) {
    return baseUrl + '/suggestions/' + suggestion_id
}

export function putASuggestionIntoUsedModeEndpoint(suggestion_id) {
    return baseUrl + '/suggestions/' + suggestion_id + '/use'
}

export function putASuggestionIntoActiveModeEndpoint(suggestion_id) {
    return baseUrl + '/suggestions/' + suggestion_id + '/activate'
}

export function postASuggestionRemovalEndpoint(suggestion_id) {
    return baseUrl + '/suggestions/' + suggestion_id + '/activate'
}

export function postANewUserEndpoint() {
    return baseUrl + '/user/'
}

export function postAUserRemovalEndpoint(user_id) {
    return baseUrl + '/user/' + user_id + '/remove'
}

export function login() {
    return baseUrl + '/login'
}

export default baseUrl;