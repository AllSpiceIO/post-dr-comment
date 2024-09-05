#! /usr/bin/env -S python3

"""
post_dr_comment.py: Post a comment to an AllSpice Hub Design Review.
"""

import argparse
import logging
import os
import sys
import yaml

from typing import Tuple

from allspice import AllSpice, Comment, DesignReview

COMMENT_IDENTIFIER = "<!-- AllSpice Hub Auto-DR Comment -->"

logger = logging.getLogger(__name__)


def parse_bool(input: str | bool) -> bool:
    """
    Parse a YAML-like boolean string as a boolean.
    """

    if isinstance(input, bool):
        return input
    if input.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif input.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError(
            "One of: yes, no, true, false, t, f, y, n, 1, 0 expected."
        )


def parse_front_matter(comment_body: str) -> Tuple[dict, str]:
    """
    Check if the comment body has a front matter and parse it.

    Returns the front matter as a dictionary and the comment body without the
    front matter.

    If the front matter is empty or missing, the front matter dictionary will
    be empty.
    """

    front_matter = {}
    found_front_matter = False
    stripped_comment_body = comment_body.strip()

    if stripped_comment_body.startswith("---"):
        split_comment = stripped_comment_body.split("---", 2)
        if len(split_comment) == 3:
            found_front_matter = True
            try:
                front_matter = yaml.safe_load(split_comment[1])
                comment_body = split_comment[2].lstrip()
                found_front_matter = True
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse front matter: {e}")

    if not found_front_matter:
        logger.info("No front matter found in comment body.")

    return front_matter, comment_body


def upsert_comment(design_review: DesignReview, comment_body: str) -> Comment:
    """
    Upsert a comment on a Design Review.
    If a comment with the same identifier already exists, update the existing
    comment. Otherwise, create a new comment.

    Returns the created or updated comment.
    """

    existing_comment = None
    comments = design_review.get_comments()
    updated_comment_body = f"{COMMENT_IDENTIFIER}\n{comment_body}"

    for comment in comments:
        if COMMENT_IDENTIFIER in comment.body:
            existing_comment = comment
            break

    if existing_comment:
        logger.info("Updating existing comment.")
        existing_comment.body = updated_comment_body
        existing_comment.commit()

        return existing_comment
    else:
        logger.info("Creating new comment.")
        return design_review.create_comment(updated_comment_body)


def upsert_attachments(comment: Comment, attachments: list[str]):
    """
    Upsert attachments to a comment.

    This clears all existing attachments and then adds new attachments.
    """

    existing_attachments = comment.get_attachments()
    for attachment in existing_attachments:
        comment.delete_attachment(attachment)

    for attachment in attachments:
        with open(attachment, "rb") as f:
            try:
                comment.create_attachment(f)
            except Exception as e:
                if "500" in str(e):
                    logger.error(
                        f"Failed to upload attachment {attachment}. "
                        "The file may be too large, or it may be of a file type "
                        "that is not supported by the AllSpice Hub."
                    )
                    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--allspice-hub-url",
        required=False,
        default="https://hub.allspice.io",
        help="The URL of the AllSpice Hub DR to post the comment to.",
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="The repository that the design review is associated with.",
    )
    parser.add_argument(
        "--design-review-number",
        required=True,
        help="The number of the design review to post the comment to.",
    )
    parser.add_argument(
        "--comment-path",
        required=True,
        help="The path to the Comment Markdown file.",
    )
    parser.add_argument(
        "--reuse-existing-comment",
        required=False,
        default=True,
        type=parse_bool,
        help="Whether to reuse an existing comment if it exists.",
    )
    parser.add_argument(
        "--log-level",
        required=False,
        default="INFO",
        help="The logging level to use.",
    )

    token = os.getenv("ALLSPICE_AUTH_TOKEN")
    if not token:
        raise ValueError("ALLSPICE_AUTH_TOKEN environment variable not set.")

    args = parser.parse_args()

    logger.setLevel(args.log_level.upper())
    client = AllSpice(
        args.allspice_hub_url,
        token_text=token,
        log_level=args.log_level.upper(),
    )
    owner, repo = args.repository.split("/")
    design_review = DesignReview.request(client, owner, repo, args.design_review_number)

    with open(args.comment_path, "r") as f:
        comment_body = f.read()

    front_matter, comment_body = parse_front_matter(comment_body)
    attachments = []
    if front_matter:
        logger.debug(f"Front matter: {front_matter}")

        if "attachments" in front_matter:
            attachments = front_matter["attachments"]

    if args.reuse_existing_comment:
        comment = upsert_comment(design_review, comment_body)
    else:
        comment = design_review.create_comment(comment_body)

    if attachments:
        upsert_attachments(comment, attachments)

    logger.info("Comment posted successfully.")


if __name__ == "__main__":
    main()
