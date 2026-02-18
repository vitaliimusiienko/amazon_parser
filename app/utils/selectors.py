class AmazonSelectors:
    TITLE = [
        "#productTitle",
        "#title",
        "span#productTitle"
        ]
    
    PRICE = [
        ".apexPriceToPay span.a-offscreen",
        ".priceToPay span.a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-color-price", 
        "#tp_price_block_total_price_ww .a-offscreen",
        "span.a-price:not(.a-text-strike) span.a-offscreen"
    ]
    
    LIST_PRICE = [
        ".a-text-price .a-offscreen",
        ".a-price.a-text-strike .a-offscreen",
        "#priceblock_strike",
        "span[data-a-strike='true'] .a-offscreen"
    ]

    PRICE_CONTAINERS = [
        "#corePrice_feature_div", 
        "#desktop_buybox",        
        "#price"               
    ]
    
    RATING = [
        "#acrPopover",
        "i[data-hook='average-star-rating'"
        ]
    
    REVIEWS_COUNT = ["#acrCustomerReviewText"]
    
    PRIME_LOGO = [
        "i.a-icon-prime",
        "span:has-text('Prime')",
        "img[alt='Amazon Prime']"
    ]
    
    BEST_SELLERS_RANK = [
        "#SalesRank",
        "th:has-text('Best Sellers Rank') + td",
        "li:has-text('Best Sellers Rank')"
    ]
    
    BULLET_POINTS = ["#feature-bullets ul li span.a-list-item"]
    
    MAIN_IMAGE = [
        "#landingImage",
        "#imgBlkFront"
        ]