class Messages:
    # general info messages
    process_terminated = "Process terminated. Send /createpost to restart."
    invalid_command = "Invalid command. Send /cancel to cancel this post."
    invalid_options = "Please choose from the options provided below."
    invalid_response = "Invalid response. Send /createpost to begin new post."
    invalid_range = "Please choose a number from 0 to 10~"
    system_error = "Something went wrong oof."
    unknown_text = "Hi, how can I help? You can choose an option from my command menu. Send /createpost to begin new " \
                   "post."

    # default messages
    welcome = "Welcome to Trybe!\n" \
              "I'm here to help you with your post.\n" \
              "Send me:\n" \
              "/createpost - to make a post\n" \
              "/cancel - to terminate post\n" \
              "/checkpost - to check post availability\n" \
              "/markpost - to mark your post as fulfilled"
    thank_you = "Thank you for being a part of the Trybe community! Your offer/request has successfully been posted " \
                "to the Trybe Services channel @RUAOK. "

    # question messages
    ask_name = "What's your name?"
    ask_username = "What's your telegram username?"
    ask_type = "Would you like to make an offer or a request today?"
    ask_offer_item_name = "Give a name for the item or service you are offering!"
    ask_request_item_name = "Give a name for the item or service you are requesting for."
    ask_item_description = "Give a short description for the item or service you are requesting for."
    ask_condition = "Is your item new or used?"
    ask_condition_rating = "Out of 10, what is the condition of the item or the proficiency of your service?"

    # post checking messages
    check_post = "Which post would you like to check? Please give me the post number indicated at the top of the post."
    check_post_expired = "Oh no, the offer/request you have checked is no longer available :("
    check_post_not_expired = "Great! The offer/request you have checked is still available."
    mark_post = "Which post would you like to mark completed? Please give me the post number indicated at the top of " \
                "the your post."
    mark_post_success = "Success! Your post has been marked as expired."
    unauthorised_edit = "Oops, you cannot mark a post as expired if you are not the post owner!"
    post_not_found = "Oh no, we can't find the post in our database!"
