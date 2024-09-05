# Post Comment on a Design Review

Post a comment on a Design Review using a markdown file as the source of the
comment on AllSpice Hub using
[AllSpice Actions](https://learn.allspice.io/docs/actions-cicd).

## Usage

Add the following step to your actions:

```yaml
- name: Post Comment on Design Review
  uses: https://hub.allspice.io/Actions/post-dr-comment@v0.1
  with:
    # The path to the markdown file containing the comment body.
    comment_path: path/to/comment.md
```

### Important Notes

1. This action works only when used in a workflow triggered by a Design Review,
   as it will automatically pick up the associated design review.
2. By default, successive runs of the action will edit the same comment.
3. This action also reads YAML frontmatter from the markdown file to post
   attachments to the posted comment.

### Customizing the Comment Content

The action uses a markdown file as the source of the comment body. You can
create a markdown file in your repository and specify its path using the
`comment_path` input.

Example `comment.md`:

```markdown
---
attachments:
  - path/to/attachment1.png
  - path/to/attachment2.pdf
---

# Comment Title

This is the body of the comment.

- Point 1
- Point 2
- Point 3

[Link to more information](https://example.com)
```

The YAML frontmatter at the beginning of the file (between `---`) can be used
to specify attachments that will be added to the comment. The YAML frontmatter
is optional, and when present, isn't included in the posted comment's body.

### Reusing Existing Comments

By default, the action will reuse the existing comment made by this action in
successive runs. This behavior can be controlled using the
`reuse_existing_comment` input. Set it to 'False' if you want to create a new
comment on each run.

### Debugging

If you encounter any issues or need more detailed information about the
action's execution, you can set the `log_level` input to 'DEBUG' for more
verbose logging.

## SSL

If your instance is running on a self-signed certificate, you can tell the
action to use your certificate by setting the `REQUESTS_CA_BUNDLE` environment
variable.

```yaml
- name: Post Comment on Design Review
  uses: https://hub.allspice.io/Actions/post-dr-comment@v0.1
  with:
    comment_path: path/to/comment.md
  env:
    REQUESTS_CA_BUNDLE: /path/to/your/certificate.cert
```

For more information about AllSpice Actions and how to use them in your
workflows, please refer to the
[AllSpice Documentation](https://learn.allspice.io/docs/actions-cicd).
