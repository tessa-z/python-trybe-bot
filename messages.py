class Messages:
    # general info messages
    process_terminated = "I just cancelled the process. Send /createpost to restart."
    invalid_command = "Hm.. I don't know what you mean."
    invalid_options = "Please choose from the options provided below."
    invalid_response = "I don't get what you mean. Cancelling process.."
    invalid_range = "Please choose a number from 0 to 10~"
    system_error = "Something went wrong oof. Thanks for finding the bug!"
    unknown_text = "Hi, how can I help? You can choose an option from my command menu."

    # default messages
    welcome = "Welcome to Trybe!\n" \
              "I'm here to help you with your post.\n" \
              "Send me:\n" \
              "/createpost - to make a new post\n" \
              "/checkpost - to check post availability\n" \
              "/markpost - to mark post as fulfilled\n"\
              "/cancel - to cancel the current process"
    thank_you = "Thank you for being a part of the Trybe community! Your offer/request has successfully been posted " \
                "to the Trybe Services channel @RUAOK. "

    # question messages
    ask_name = "What's your name?"
    ask_username_0 = "Would you like to leave your telegram username for contact purposes?"
    ask_username_1 = "I'll only let people interested in your post know to contact you :)"
    ask_username_rejected_0 = "I need you to leave your username so that you can be contacted if someone is " \
                              "interested in your post."
    ask_username_rejected_1 = "Sorry for the inconvenience :("
    ask_username_missing_0 = "Oops, seems like you haven't set a username yet"
    ask_username_missing_1 = "You can do so by going to your Telegram Settings page"
    ask_username_missing_2 = "Come back and /createpost when you're ready!"
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
    check_post_getusername = "Would you like to contact the owner of the post?"
    check_post_sendusername = "You can contact them at: @"
    check_post_nogetusername = "Sure, just let me know when you are ready!"

    mark_post = "Which post would you like to mark completed? Please give me the post number indicated at the top of " \
                "the your post."
    mark_post_success = "Success! Your post has been marked as expired."
    unauthorised_edit = "Oops, you cannot mark a post as expired if you are not the post owner!"
    post_not_found = "Oh no, I can't find the post in my database!"
