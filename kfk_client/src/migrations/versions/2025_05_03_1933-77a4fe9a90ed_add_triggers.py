"""Add Triggers

Revision ID: 77a4fe9a90ed
Revises: cfbe00680a56
Create Date: 2025-05-03 19:33:14.781686

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "77a4fe9a90ed"
down_revision: Union[str, None] = "cfbe00680a56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

######################
## Triggers (Users) ##
######################

# SQL-query to create the trigger
create_trigger_users_sql = """
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_updated_at
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
"""

########################
## Triggers (emails) ##
########################

# SQL-query to create the trigger
create_trigger_emails_sql = """
CREATE OR REPLACE FUNCTION set_updated_at_emails()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_updated_at_emails
BEFORE INSERT OR UPDATE ON emails
FOR EACH ROW
EXECUTE FUNCTION set_updated_at_emails();
"""


################
## Migrations ##
################


def upgrade() -> None:

    op.execute(
        """
    CREATE OR REPLACE FUNCTION set_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at := NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trigger_set_updated_at
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION set_updated_at_emails()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at := NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trigger_set_updated_at_emails
    BEFORE INSERT OR UPDATE ON emails
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at_emails();
    """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trigger_set_updated_at ON users;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at;")

    op.execute("DROP TRIGGER IF EXISTS trigger_set_updated_at_emails ON emails;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at_emails;")
