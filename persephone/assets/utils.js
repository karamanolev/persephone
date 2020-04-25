export function formatSha(sha) {
    if (!sha) {
        return '';
    }
    return sha.substr(0, 7);
}
