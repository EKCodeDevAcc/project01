-- Adminer 4.6.3-dev PostgreSQL dump

\connect "d50m2e3k3ikg9p";

DROP TABLE IF EXISTS "comments";
DROP SEQUENCE IF EXISTS comments_comment_id_seq;
CREATE SEQUENCE comments_comment_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."comments" (
    "comment_id" integer DEFAULT nextval('comments_comment_id_seq') NOT NULL,
    "username" character varying NOT NULL,
    "zipcode" character varying NOT NULL,
    "comment" text NOT NULL,
    CONSTRAINT "comments_pkey" PRIMARY KEY ("comment_id"),
    CONSTRAINT "comments_zipcode_fkey" FOREIGN KEY (zipcode) REFERENCES zips(zipcode) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "members";
DROP SEQUENCE IF EXISTS members_id_seq;
CREATE SEQUENCE members_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."members" (
    "id" integer DEFAULT nextval('members_id_seq') NOT NULL,
    "username" character varying NOT NULL,
    "password" character varying NOT NULL,
    CONSTRAINT "members_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "zips";
CREATE TABLE "public"."zips" (
    "zipcode" character varying NOT NULL,
    "city" character varying NOT NULL,
    "state" character varying NOT NULL,
    "latitude" numeric NOT NULL,
    "longitude" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "zips_pkey" PRIMARY KEY ("zipcode")
) WITH (oids = false);


-- 2018-07-12 20:42:34.811371+00
