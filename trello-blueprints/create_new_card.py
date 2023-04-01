import argparse
import sys
import requests
import json
try:
    import errors
except BaseException:
    from . import errors


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--access-key', dest='access_key', required=True)
    parser.add_argument('--access-token', dest='access_token', required=True)
    parser.add_argument('--board-name', dest='board_name', required=True)
    parser.add_argument('--list-name', dest='list_name', required=True)
    parser.add_argument('--card-title', dest='card_title', required=False)
    parser.add_argument('--card-description', dest='card_description', required=False)
    parser.add_argument('--card-position', dest='card_position', required=False)
    parser.add_argument('--card-due-date', dest='card_due_date', required=False)
    parser.add_argument('--card-start-date', dest='card_start_date', required=False)
    parser.add_argument('--card-due-complete', dest='card_due_complete', required=False)
    parser.add_argument('--card-members-assigned', dest='card_members_assigned', default='', required=False)
    parser.add_argument('--card-labels', dest='card_labels', default='', required=False)

    args = parser.parse_args()
    return args


def get_board_id(access_key: str, access_token: str, board_name: str) -> list:
    # Make request to get all user boards and return id of board with same name as user arg
    url = 'https://api.trello.com/1/members/me/boards'
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': access_key,
        'token': access_token
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )

    if response.status_code == 200:
        print('Successfully got user boards')
        user_boards = response.json()
        for board in user_boards:
            if board['name'] == board_name:
                return board['id']
        print(f"No board named '{board_name}' found in Trello response. Ensure you have access to '{board_name}'.")
        sys.exit()
    elif response.status_code == 401:
        print("You do not have the required permissions. Check your Trello API key and Trello API token.")
        sys.exit(errors.EXIT_CODE_INVALID_CREDENTIALS)
    elif response.status_code == 400:
        print('Trello responded with Bad Request Error. ',
              f'Response message: {response.text}')
        sys.exit(errors.EXIT_CODE_BAD_REQUEST)
    else:
        print(
            f'An unknown HTTP Status {response.status_code} and response occurred when attempting your request: ',
            f'{response.text}')
        sys.exit(errors.EXIT_CODE_UNKNOWN_ERROR)


def get_list_id(access_key: str, access_token: str, board_id: str, board_name: str, list_name: str) -> list:
    url = f'https://api.trello.com/1/boards/{board_id}/lists'
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': access_key,
        'token': access_token
    }
    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )

    if response.status_code == 200:
        print('Successfully got board lists')
        board_lists = response.json()
        for list in board_lists:
            if list['name'] == list_name:
                return list['id']
        print(f"No list named '{list_name}' found in Trello response. Ensure that '{list_name}' exists on '{board_name}'.")
        sys.exit()
    elif response.status_code == 401:
        print("You do not have the required permissions. Check your Trello API key and Trello API token.")
        sys.exit(errors.EXIT_CODE_INVALID_CREDENTIALS)
    elif response.status_code == 400:
        print('Trello responded with Bad Request Error. ',
              f'Response message: {response.text}')
        sys.exit(errors.EXIT_CODE_BAD_REQUEST)
    else:
        print(
            f'An unknown HTTP Status {response.status_code} and response occurred when attempting your request: ',
            f'{response.text}')
        sys.exit(errors.EXIT_CODE_UNKNOWN_ERROR)


def get_all_member_ids(access_key: str, access_token: str, board_id: str) -> list:
    url = f'https://api.trello.com/1/boards/{board_id}/memberships'
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': access_key,
        'token': access_token
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )

    if response.status_code == 200:
        print('Successfully got board members')
        members = response.json()
        return [member['idMember'] for member in members]
    else:
        return []


def get_member(access_key: str, access_token: str, member_id: str) -> dict:
    url = f'https://api.trello.com/1/members/{member_id}'
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': access_key,
        'token': access_token
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )

    if response.status_code == 200:
        print(f'Successfully got member {member_id}')
        member = response.json()
        return member
    else:
        return {}


def get_member_ids(access_key: str, access_token: str, board_id: str, card_member_usernames: str) -> list:
    card_member_usernames = card_member_usernames.split(',')
    all_member_ids = get_all_member_ids(access_key, access_token, board_id)
    member_ids = []
    for member_id in all_member_ids:
        member = get_member(access_key, access_token, member_id)
        if 'username' in member:
            if member['username'] in card_member_usernames:
                member_ids.append(member_id)
    return member_ids


def get_label_ids(access_key: str, access_token: str, board_id: str, card_label_names: str) -> list:
    card_label_names = card_label_names.split(',')
    url = f'https://api.trello.com/1/boards/{board_id}/labels'
    query = {
        'key': access_key,
        'token': access_token
    }

    response = requests.request(
        "GET",
        url,
        params=query
    )

    if response.status_code == 200:
        print('Successfully got card labels')
        card_labels = response.json()
        return [label['id'] for label in card_labels if label['name'] in card_label_names]
    elif response.status_code == 401:
        print("You do not have the required permissions. Check your Trello API key and Trello API token.")
        sys.exit(errors.EXIT_CODE_INVALID_CREDENTIALS)
    elif response.status_code == 400:
        print('Trello responded with Bad Request Error. ',
              f'Response message: {response.text}')
        sys.exit(errors.EXIT_CODE_BAD_REQUEST)
    else:
        print(
            f'An unknown HTTP Status {response.status_code} and response occurred when attempting your request: ',
            f'{response.text}')
        sys.exit(errors.EXIT_CODE_UNKNOWN_ERROR)


def create_new_card(access_key: str, access_token: str, list_id: str, card_title: str, card_description: str, card_position: str, card_due: str, card_start: str, card_due_complete: bool, card_member_ids: list, card_label_ids: list) -> None:
    url = "https://api.trello.com/1/cards"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'key': access_key,
        'token': access_token,
        'idList': list_id,
        'name': card_title,
        'desc': card_description,
        'pos': card_position,
        'due': card_due,
        'start': card_start,
        'dueComplete': card_due_complete,
        'idMembers': ','.join(card_member_ids),
        'idLabels':  ','.join(card_label_ids)
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        params=query
    )

    if response.status_code == 200:
        print('Successfully created new card')
    elif response.status_code == 401:
        print("You do not have the required permissions. Check your Trello API key and Trello API token.")
        sys.exit(errors.EXIT_CODE_INVALID_CREDENTIALS)
    elif response.status_code == 400:
        print('Trello responded with Bad Request Error. ',
              f'Response message: {response.text}')
        sys.exit(errors.EXIT_CODE_BAD_REQUEST)
    else:
        print(
            f'An unknown HTTP Status {response.status_code} and response occurred when attempting your request: ',
            f'{response.text}')
        sys.exit(errors.EXIT_CODE_UNKNOWN_ERROR)


def main() -> None:
    args = get_args()
    access_key = args.access_key
    access_token = args.access_token
    board_name = args.board_name
    list_name = args.list_name
    card_title = args.card_title
    card_description = args.card_description
    card_position = args.card_position
    card_due = args.card_due_date
    card_start = args.card_start_date
    card_due_complete = args.card_due_complete
    card_member_usernames = args.card_members_assigned
    card_label_names = args.card_labels

    board_id = get_board_id(access_key, access_token, board_name)
    list_id = get_list_id(access_key, access_token, board_id, board_name, list_name)
    card_member_ids = get_member_ids(access_key, access_token, board_id, card_member_usernames)
    card_label_ids = get_label_ids(access_key, access_token, board_id, card_label_names)

    create_new_card(
        access_key,
        access_token,
        list_id,
        card_title,
        card_description,
        card_position,
        card_due, card_start,
        card_due_complete,
        card_member_ids,
        card_label_ids
    )


if __name__ == "__main__":
    main()
