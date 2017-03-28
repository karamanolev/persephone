from builds.models import Screenshot


def sort_screenshots_by_relevance(screenshots):
    state_relevance_order = [
        Screenshot.STATE_DIFFERENT,
        Screenshot.STATE_DELETED,
        Screenshot.STATE_NEW,
        Screenshot.STATE_PENDING,
        Screenshot.STATE_MATCHING,
    ]

    def _key_screenshot(a):
        return state_relevance_order.index(a.state), a.name

    screenshots.sort(key=_key_screenshot)
