class AmazonSelectors:
    TITLE = ["#productTitle", "#title", "span#productTitle"]

    PRICE_CONTAINERS = "#corePriceDisplay_desktop_feature_div"

    PRICE = ["span.a-price span.a-offscreen", ".a-price-whole"]

    LIST_PRICE = [
        "#corePriceDisplay_desktop_feature_div span.a-price.a-text-price span.a-offscreen",
    ]

    DISCOUNT_PERCENTAGE = ".savingsPercentage"

    RATING = ["#acrPopover", "i[data-hook='average-star-rating'"]

    REVIEWS_COUNT = ["#acrCustomerReviewText"]

    PRIME_LOGO = ["i.a-icon-prime", "span:has-text('Prime')", "img[alt='Amazon Prime']"]

    BEST_SELLERS_RANK = [
        "#SalesRank",
        "th:has-text('Best Sellers Rank') + td",
        "li:has-text('Best Sellers Rank')",
    ]

    BULLET_POINTS = ["#feature-bullets ul li span.a-list-item"]

    MAIN_IMAGE = ["#landingImage", "#imgBlkFront"]
