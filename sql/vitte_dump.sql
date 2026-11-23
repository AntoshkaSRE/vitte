--
-- PostgreSQL database dump
--

\restrict Znj74wsN0aw90GydGGC9TMbVGqTfahdZtyjL7G2D21adwgoWWvsZww3URXttGh1

-- Dumped from database version 17.12
-- Dumped by pg_dump version 17.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: academic_periods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.academic_periods (
    id integer NOT NULL,
    academic_year character varying(9) NOT NULL,
    semester smallint NOT NULL,
    title character varying(60) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    CONSTRAINT academic_periods_semester_check CHECK ((semester = ANY (ARRAY[1, 2])))
);


--
-- Name: academic_periods_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.academic_periods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: academic_periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.academic_periods_id_seq OWNED BY public.academic_periods.id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_id integer,
    action character varying(40) NOT NULL,
    details text DEFAULT ''::text NOT NULL,
    ip_address character varying(45) DEFAULT ''::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: cache_entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cache_entries (
    cache_key character varying(200) NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: dashboard_widgets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_widgets (
    id integer NOT NULL,
    dashboard_id integer NOT NULL,
    indicator_id integer NOT NULL,
    title character varying(120) NOT NULL,
    chart_type character varying(10) NOT NULL,
    "position" smallint DEFAULT 1 NOT NULL,
    CONSTRAINT dashboard_widgets_chart_type_check CHECK (((chart_type)::text = ANY ((ARRAY['bar'::character varying, 'line'::character varying, 'pie'::character varying, 'doughnut'::character varying, 'kpi'::character varying])::text[])))
);


--
-- Name: dashboard_widgets_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_widgets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_widgets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_widgets_id_seq OWNED BY public.dashboard_widgets.id;


--
-- Name: dashboards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboards (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    title character varying(120) NOT NULL,
    description text DEFAULT ''::text NOT NULL,
    min_role_level smallint DEFAULT 1 NOT NULL
);


--
-- Name: dashboards_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboards_id_seq OWNED BY public.dashboards.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    faculty_id integer NOT NULL,
    name character varying(160) NOT NULL,
    head_name character varying(120) DEFAULT ''::character varying NOT NULL
);


--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: directions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.directions (
    id integer NOT NULL,
    faculty_id integer NOT NULL,
    code character varying(12) NOT NULL,
    name character varying(160) NOT NULL,
    level character varying(20) DEFAULT 'Бакалавриат'::character varying NOT NULL
);


--
-- Name: directions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.directions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: directions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.directions_id_seq OWNED BY public.directions.id;


--
-- Name: faculties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.faculties (
    id integer NOT NULL,
    code character varying(10) NOT NULL,
    name character varying(160) NOT NULL,
    short_name character varying(40) NOT NULL,
    dean_name character varying(120) DEFAULT ''::character varying NOT NULL,
    description text DEFAULT ''::text NOT NULL
);


--
-- Name: faculties_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.faculties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: faculties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.faculties_id_seq OWNED BY public.faculties.id;


--
-- Name: feedback_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feedback_messages (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    email character varying(120) NOT NULL,
    subject character varying(160) NOT NULL,
    message text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    is_processed boolean DEFAULT false NOT NULL
);


--
-- Name: feedback_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feedback_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feedback_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feedback_messages_id_seq OWNED BY public.feedback_messages.id;


--
-- Name: group_performance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.group_performance (
    id integer NOT NULL,
    group_id integer NOT NULL,
    period_id integer NOT NULL,
    students integer NOT NULL,
    avg_grade numeric(3,2) NOT NULL,
    passed_percent numeric(5,2) NOT NULL,
    CONSTRAINT group_performance_avg_grade_check CHECK (((avg_grade >= (2)::numeric) AND (avg_grade <= (5)::numeric))),
    CONSTRAINT group_performance_passed_percent_check CHECK (((passed_percent >= (0)::numeric) AND (passed_percent <= (100)::numeric))),
    CONSTRAINT group_performance_students_check CHECK ((students >= 0))
);


--
-- Name: group_performance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.group_performance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: group_performance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.group_performance_id_seq OWNED BY public.group_performance.id;


--
-- Name: indicator_values; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.indicator_values (
    id integer NOT NULL,
    indicator_id integer NOT NULL,
    period_id integer NOT NULL,
    faculty_id integer NOT NULL,
    value numeric(14,2) NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: indicator_values_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.indicator_values_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: indicator_values_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.indicator_values_id_seq OWNED BY public.indicator_values.id;


--
-- Name: indicators; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.indicators (
    id integer NOT NULL,
    code character varying(30) NOT NULL,
    name character varying(160) NOT NULL,
    unit character varying(20) NOT NULL,
    category character varying(40) NOT NULL,
    description text DEFAULT ''::text NOT NULL,
    is_public boolean DEFAULT false NOT NULL
);


--
-- Name: indicators_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.indicators_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: indicators_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.indicators_id_seq OWNED BY public.indicators.id;


--
-- Name: integration_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.integration_settings (
    key character varying(40) NOT NULL,
    value text DEFAULT ''::text NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: news; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.news (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    summary character varying(400) NOT NULL,
    body text NOT NULL,
    published_at timestamp without time zone DEFAULT now() NOT NULL,
    author_id integer,
    is_published boolean DEFAULT true NOT NULL
);


--
-- Name: news_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.news_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.news_id_seq OWNED BY public.news.id;


--
-- Name: report_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.report_history (
    id integer NOT NULL,
    user_id integer NOT NULL,
    report_type character varying(30) NOT NULL,
    params jsonb DEFAULT '{}'::jsonb NOT NULL,
    file_format character varying(10) NOT NULL,
    file_name character varying(200) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: report_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.report_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: report_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.report_history_id_seq OWNED BY public.report_history.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(80) NOT NULL,
    description text DEFAULT ''::text NOT NULL,
    level smallint DEFAULT 1 NOT NULL
);


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: study_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.study_groups (
    id integer NOT NULL,
    direction_id integer NOT NULL,
    name character varying(30) NOT NULL,
    course smallint NOT NULL,
    study_form character varying(20) DEFAULT 'Очная'::character varying NOT NULL,
    CONSTRAINT study_groups_course_check CHECK (((course >= 1) AND (course <= 6)))
);


--
-- Name: study_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.study_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: study_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.study_groups_id_seq OWNED BY public.study_groups.id;


--
-- Name: sync_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sync_log (
    id integer NOT NULL,
    started_at timestamp without time zone DEFAULT now() NOT NULL,
    finished_at timestamp without time zone,
    source character varying(20) NOT NULL,
    status character varying(10) DEFAULT 'running'::character varying NOT NULL,
    rows_loaded integer DEFAULT 0 NOT NULL,
    message text DEFAULT ''::text NOT NULL,
    started_by integer
);


--
-- Name: sync_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sync_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sync_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sync_log_id_seq OWNED BY public.sync_log.id;


--
-- Name: uploaded_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.uploaded_files (
    id integer NOT NULL,
    user_id integer NOT NULL,
    original_name character varying(200) NOT NULL,
    stored_name character varying(80) NOT NULL,
    size_bytes integer NOT NULL,
    uploaded_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: uploaded_files_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.uploaded_files_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: uploaded_files_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.uploaded_files_id_seq OWNED BY public.uploaded_files.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    login character varying(40) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(120) NOT NULL,
    email character varying(120) DEFAULT ''::character varying NOT NULL,
    role_id integer NOT NULL,
    faculty_id integer,
    is_active boolean DEFAULT true NOT NULL,
    preferences jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    last_login timestamp without time zone
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: academic_periods id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.academic_periods ALTER COLUMN id SET DEFAULT nextval('public.academic_periods_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: dashboard_widgets id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_widgets ALTER COLUMN id SET DEFAULT nextval('public.dashboard_widgets_id_seq'::regclass);


--
-- Name: dashboards id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboards ALTER COLUMN id SET DEFAULT nextval('public.dashboards_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: directions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.directions ALTER COLUMN id SET DEFAULT nextval('public.directions_id_seq'::regclass);


--
-- Name: faculties id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties ALTER COLUMN id SET DEFAULT nextval('public.faculties_id_seq'::regclass);


--
-- Name: feedback_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback_messages ALTER COLUMN id SET DEFAULT nextval('public.feedback_messages_id_seq'::regclass);


--
-- Name: group_performance id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_performance ALTER COLUMN id SET DEFAULT nextval('public.group_performance_id_seq'::regclass);


--
-- Name: indicator_values id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator_values ALTER COLUMN id SET DEFAULT nextval('public.indicator_values_id_seq'::regclass);


--
-- Name: indicators id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicators ALTER COLUMN id SET DEFAULT nextval('public.indicators_id_seq'::regclass);


--
-- Name: news id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.news ALTER COLUMN id SET DEFAULT nextval('public.news_id_seq'::regclass);


--
-- Name: report_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_history ALTER COLUMN id SET DEFAULT nextval('public.report_history_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: study_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_groups ALTER COLUMN id SET DEFAULT nextval('public.study_groups_id_seq'::regclass);


--
-- Name: sync_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sync_log ALTER COLUMN id SET DEFAULT nextval('public.sync_log_id_seq'::regclass);


--
-- Name: uploaded_files id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_files ALTER COLUMN id SET DEFAULT nextval('public.uploaded_files_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: academic_periods; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.academic_periods (id, academic_year, semester, title, start_date, end_date) FROM stdin;
1	2023/2024	1	Осенний семестр 2023/2024	2023-09-01	2024-01-31
2	2023/2024	2	Весенний семестр 2023/2024	2024-02-01	2024-06-30
3	2024/2025	1	Осенний семестр 2024/2025	2024-09-01	2025-01-31
4	2024/2025	2	Весенний семестр 2024/2025	2025-02-01	2025-06-30
5	2025/2026	1	Осенний семестр 2025/2026	2025-09-01	2026-01-31
6	2025/2026	2	Весенний семестр 2025/2026	2026-02-01	2026-06-30
7	2026/2027	1	Осенний семестр 2026/2027	2026-09-01	2027-01-31
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_log (id, user_id, action, details, ip_address, created_at) FROM stdin;
1	1	login	Вход в систему	127.0.0.1	2026-11-23 23:08:57.542956
2	3	report	Отчёт performance (xlsx)	127.0.0.1	2026-11-23 23:08:57.542956
3	2	login	Вход в систему	127.0.0.1	2026-11-23 23:17:45.802776
4	2	dashboard	Просмотр дашборда kpi	127.0.0.1	2026-11-23 23:17:45.944336
5	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:21.048696
6	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:21.52272
7	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:21.948206
8	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:22.358267
9	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:22.879648
10	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:23.20631
11	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.330827
12	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.333468
13	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.50525
14	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.555966
15	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.67732
16	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.735443
17	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.782536
18	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.955114
19	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:25.9588
20	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:26.035039
21	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:26.682259
22	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:26.782005
23	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:26.878222
24	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:26.923848
25	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.141713
26	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.234286
27	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.24967
28	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.272977
29	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.338135
30	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.410466
31	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.950444
32	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:27.988853
33	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.078083
34	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.200335
35	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.436719
36	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.52206
37	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.526038
38	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.56066
39	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.569516
40	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:28.751631
41	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.119983
42	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.251714
43	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.286071
44	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.454878
45	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.67278
46	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.694852
47	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.782019
48	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.896051
49	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:29.91758
50	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:30.097683
51	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:30.358094
52	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:30.395513
53	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:30.549264
54	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:30.580536
55	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:30.879598
56	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:30.993294
57	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.010991
58	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.080606
59	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.160057
60	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.4973
61	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.588803
62	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.668135
63	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.690733
64	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:31.727479
65	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:32.28345
66	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:32.292269
67	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:32.320607
68	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:32.346318
69	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:32.415711
70	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:32.517195
71	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:37.575325
72	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:37.947741
73	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:38.085849
74	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:38.230437
75	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:38.506702
76	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:38.530239
77	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:38.81375
78	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:39.045412
79	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:39.056094
80	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:39.110656
81	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:39.247934
82	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:39.590104
83	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:39.722616
84	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:40.0788
85	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:40.117668
86	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:40.663989
87	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:40.647981
88	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:40.909197
89	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.209698
90	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.293561
91	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.310176
92	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.335011
93	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.364408
94	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.445851
95	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.447481
96	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:41.522534
97	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:41.939719
98	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:42.161195
99	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:42.351272
100	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:42.416637
101	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:42.544844
102	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:42.584874
103	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:42.598423
104	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:42.645038
105	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:42.913677
106	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:43.108096
107	2	login	Вход в систему	127.0.0.1	2026-11-23 23:18:43.225644
108	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:43.814766
109	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:43.932462
110	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:43.960584
111	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:44.163021
112	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:44.179819
113	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:44.598004
114	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:44.900233
115	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:45.091364
116	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:45.235128
117	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:45.36464
118	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:45.56435
119	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:45.943106
120	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.066323
121	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.083053
122	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.117329
123	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.19508
124	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.277874
125	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.341215
126	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.383486
127	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.439154
128	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.440724
129	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.685149
130	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.866765
131	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:46.95119
132	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.008966
133	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.033313
134	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.100202
135	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.509953
136	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.516822
137	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.805899
138	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.828529
139	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.840162
140	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:47.961992
141	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:48.003432
142	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:48.103824
143	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:48.627391
144	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:48.9198
145	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:49.271741
146	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:49.351055
147	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:49.581802
148	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:49.739008
149	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:49.91702
150	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.056751
151	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.073383
152	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.161188
153	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.386591
154	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.472777
155	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.484713
156	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.485974
157	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.542705
158	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.560772
159	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.798091
160	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.831329
161	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.870852
162	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:50.99996
163	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:51.044993
164	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:51.058677
165	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:51.721825
166	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:51.815401
167	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:51.968956
168	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:52.159178
169	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:52.202998
170	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:52.305374
171	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:52.460404
172	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:52.597065
173	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:52.919892
174	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:53.284902
175	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:53.874324
176	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:53.998635
177	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:54.005789
178	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:54.172984
179	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:54.328405
180	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:54.420091
181	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:54.591712
182	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:54.740926
183	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.045833
184	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.066803
185	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.14199
186	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.241659
187	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.243702
188	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.274104
189	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.403783
190	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.501779
191	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.57274
192	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.618214
193	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.750762
194	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:55.998547
195	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:56.306138
196	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:56.392356
197	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:56.49652
198	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:56.575618
199	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:56.697241
200	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:56.807789
201	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:56.811709
202	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:57.115933
203	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:57.494857
204	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:57.63502
205	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.124947
206	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.197682
207	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.208697
208	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.420938
209	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.57734
210	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.582118
211	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.680256
212	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:58.69958
213	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.108604
214	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.193125
215	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.280251
216	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.282197
217	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.330712
218	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.341348
219	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.517053
220	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.594198
221	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.611985
222	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.620179
223	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.807837
224	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:18:59.885887
225	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:00.117685
226	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:00.265865
227	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:00.327126
228	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:00.530616
229	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:00.603401
230	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:00.665287
231	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:00.692696
232	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.042129
233	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.289574
234	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.384317
235	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.548959
236	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.706867
237	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.788734
238	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.801503
239	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.873384
240	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.946024
241	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:01.971585
242	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.00744
243	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.059822
244	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.077177
245	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.103926
246	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.118117
247	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.265242
248	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.358895
249	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.398014
250	2	dashboard	Просмотр дашборда contingent	127.0.0.1	2026-11-23 23:19:02.466784
251	2	dashboard	Просмотр дашборда performance	127.0.0.1	2026-11-23 23:22:03.511312
\.


--
-- Data for Name: cache_entries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cache_entries (cache_key, payload, created_at) FROM stdin;
cmp:1:7:None	{"labels": ["ФИТ", "ФЭУ", "ЮФ", "ФП", "ФДК"], "values": [380.0, 474.0, 85.0, 126.0, 157.0]}	2026-11-23 23:17:02.015897
cmp:7:7:None	{"labels": ["ФИТ", "ФЭУ", "ЮФ", "ФП", "ФДК"], "values": [4.15, 4.2, 4.11, 4.35, 4.25]}	2026-11-23 23:17:02.038606
cmp:9:7:None	{"labels": ["ФИТ", "ФЭУ", "ЮФ", "ФП", "ФДК"], "values": [38.0, 44.0, 12.0, 12.0, 14.0]}	2026-11-23 23:17:02.04014
dyn:1:None	{"labels": ["Осенний семестр 2023/2024", "Весенний семестр 2023/2024", "Осенний семестр 2024/2025", "Весенний семестр 2024/2025", "Осенний семестр 2025/2026", "Весенний семестр 2025/2026", "Осенний семестр 2026/2027"], "values": [1141.0, 1126.0, 1130.0, 1183.0, 1180.0, 1169.0, 1222.0]}	2026-11-23 23:17:12.011136
dyn:7:None	{"labels": ["Осенний семестр 2023/2024", "Весенний семестр 2023/2024", "Осенний семестр 2024/2025", "Весенний семестр 2024/2025", "Осенний семестр 2025/2026", "Весенний семестр 2025/2026", "Осенний семестр 2026/2027"], "values": [4.14, 4.14, 4.15, 4.17, 4.19, 4.21, 4.21]}	2026-11-23 23:17:46.334672
cmp:8:7:None	{"labels": ["ФИТ", "ФЭУ", "ЮФ", "ФП", "ФДК"], "values": [91.24, 88.44, 92.54, 88.72, 92.66]}	2026-11-23 23:17:46.357214
cmp:10:7:None	{"labels": ["ФИТ", "ФЭУ", "ЮФ", "ФП", "ФДК"], "values": [62.5, 61.6, 72.6, 70.1, 52.8]}	2026-11-23 23:17:46.358419
cmp:4:7:None	{"labels": ["ФИТ", "ФЭУ", "ЮФ", "ФП", "ФДК"], "values": [110.0, 115.0, 24.0, 33.0, 45.0]}	2026-11-23 23:17:46.359478
cmp:5:7:None	{"labels": ["ФИТ", "ФЭУ", "ЮФ", "ФП", "ФДК"], "values": [12.0, 7.0, 4.0, 1.0, 3.0]}	2026-11-23 23:18:21.470436
\.


--
-- Data for Name: dashboard_widgets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_widgets (id, dashboard_id, indicator_id, title, chart_type, "position") FROM stdin;
1	1	1	Численность студентов по факультетам	bar	1
2	1	7	Динамика среднего балла	line	2
3	1	8	Доля студентов без задолженностей	bar	3
4	1	10	Доля ППС с учёной степенью	doughnut	4
5	1	4	Приём на первый курс	kpi	5
6	2	1	Численность студентов	bar	1
7	2	2	Структура очной формы	pie	2
8	2	4	Приём на первый курс	line	3
9	2	5	Отчисленные студенты	bar	4
10	2	6	Выпуск	kpi	5
11	3	7	Средний балл	line	1
12	3	8	Доля студентов без задолженностей	bar	2
13	3	5	Отчисления за период	bar	3
14	4	9	Численность ППС	bar	1
15	4	10	Доля ППС с учёной степенью	line	2
16	4	11	Плановая учебная нагрузка	bar	3
17	5	12	Научные публикации	bar	1
18	5	9	Численность ППС	pie	2
\.


--
-- Data for Name: dashboards; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboards (id, code, title, description, min_role_level) FROM stdin;
1	kpi	Ключевые показатели деятельности университета	Сводные показатели для руководства: контингент, успеваемость, кадры.	3
2	contingent	Контингент студентов	Структура и движение контингента по факультетам и периодам.	1
3	performance	Успеваемость	Успеваемость студентов по итогам сессий.	1
4	staff	Кадровый состав и нагрузка	Профессорско-преподавательский состав и учебная нагрузка.	2
5	science	Научная деятельность	Публикационная активность преподавателей.	2
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.departments (id, faculty_id, name, head_name) FROM stdin;
1	1	Кафедра информационных систем	Простомолотов Александр Сергеевич
2	1	Кафедра информационной безопасности	Громов Алексей Петрович
3	2	Кафедра экономики	Беляева Ольга Николаевна
4	2	Кафедра менеджмента	Захаров Игорь Юрьевич
5	3	Кафедра гражданского права	Фролова Татьяна Алексеевна
6	3	Кафедра уголовного права	Дроздов Николай Васильевич
7	4	Кафедра общей психологии	Никитина Анна Сергеевна
8	5	Кафедра дизайна	Куликов Артём Олегович
9	5	Кафедра рекламы и PR	Тарасова Марина Игоревна
10	4	Кафедра педагогики	Воронин Павел Дмитриевич
\.


--
-- Data for Name: directions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.directions (id, faculty_id, code, name, level) FROM stdin;
1	1	09.03.03	Прикладная информатика	Бакалавриат
2	1	09.03.01	Информатика и вычислительная техника	Бакалавриат
3	1	10.03.01	Информационная безопасность	Бакалавриат
4	2	38.03.01	Экономика	Бакалавриат
5	2	38.03.02	Менеджмент	Бакалавриат
6	2	38.03.04	Государственное и муниципальное управление	Бакалавриат
7	3	40.03.01	Юриспруденция	Бакалавриат
8	4	37.03.01	Психология	Бакалавриат
9	4	44.03.02	Психолого-педагогическое образование	Бакалавриат
10	5	42.03.01	Реклама и связи с общественностью	Бакалавриат
11	5	54.03.01	Дизайн	Бакалавриат
12	2	38.03.05	Бизнес-информатика	Бакалавриат
\.


--
-- Data for Name: faculties; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.faculties (id, code, name, short_name, dean_name, description) FROM stdin;
1	FIT	Факультет информационных технологий	ФИТ	Лебедев Сергей Игоревич	Факультет информационных технологий — структурное подразделение университета.
2	FEU	Факультет экономики и управления	ФЭУ	Миронова Елена Павловна	Факультет экономики и управления — структурное подразделение университета.
3	LAW	Юридический факультет	ЮФ	Ковалёв Дмитрий Андреевич	Юридический факультет — структурное подразделение университета.
4	PSY	Факультет психологии	ФП	Соколова Ирина Викторовна	Факультет психологии — структурное подразделение университета.
5	DES	Факультет дизайна и коммуникаций	ФДК	Орлов Михаил Сергеевич	Факультет дизайна и коммуникаций — структурное подразделение университета.
\.


--
-- Data for Name: feedback_messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feedback_messages (id, name, email, subject, message, created_at, is_processed) FROM stdin;
1	Смирнова Анна	smirnova@example.com	Вопрос по доступу	Подскажите, как получить доступ к дашборду успеваемости?	2026-11-23 23:08:57.542956	f
2	Козлов Игорь	kozlov@example.com	Предложение	Хорошо бы добавить диаграмму по формам обучения.	2026-11-23 23:08:57.542956	f
3	Фёдорова Мария	fedorova@example.com	Ошибка в данных	В показателе приёма на 2 курсе видна неточность.	2026-11-23 23:08:57.542956	f
\.


--
-- Data for Name: group_performance; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.group_performance (id, group_id, period_id, students, avg_grade, passed_percent) FROM stdin;
1	1	1	19	3.91	93.32
2	1	2	19	3.94	96.94
3	1	3	21	3.97	96.54
4	1	4	21	3.83	97.01
5	1	5	24	4.03	99.02
6	1	6	23	4.03	99.25
7	1	7	25	3.94	97.45
8	2	1	23	4.49	94.13
9	2	2	19	4.40	92.37
10	2	3	20	4.50	97.20
11	2	4	22	4.46	94.35
12	2	5	21	4.48	93.49
13	2	6	20	4.61	94.94
14	2	7	21	4.41	94.99
15	3	1	31	4.41	90.53
16	3	2	29	4.33	87.13
17	3	3	31	4.33	90.94
18	3	4	33	4.47	89.19
19	3	5	31	4.30	89.18
20	3	6	33	4.43	89.11
21	3	7	32	4.47	87.08
22	4	1	34	4.16	89.44
23	4	2	32	4.19	89.13
24	4	3	31	4.30	90.69
25	4	4	33	4.33	90.53
26	4	5	32	4.27	89.94
27	4	6	36	4.47	87.88
28	4	7	34	4.37	89.91
29	5	1	26	3.69	78.75
30	5	2	24	3.58	78.33
31	5	3	26	3.76	81.94
32	5	4	26	3.65	79.31
33	5	5	27	3.67	80.82
34	5	6	28	3.77	82.85
35	5	7	26	3.66	83.98
36	6	1	28	4.37	85.54
37	6	2	26	4.47	85.51
38	6	3	26	4.34	87.82
39	6	4	30	4.33	87.72
40	6	5	28	4.43	87.70
41	6	6	27	4.45	87.97
42	6	7	31	4.37	89.58
43	7	1	31	4.32	79.81
44	7	2	31	4.29	83.42
45	7	3	32	4.29	80.02
46	7	4	34	4.22	84.71
47	7	5	34	4.40	80.95
48	7	6	34	4.21	82.75
49	7	7	35	4.31	80.68
50	8	1	24	3.85	94.84
51	8	2	24	3.98	96.74
52	8	3	26	3.91	96.32
53	8	4	29	3.86	96.31
54	8	5	29	3.92	96.96
55	8	6	25	4.06	99.50
56	8	7	28	4.01	99.50
57	9	1	29	4.22	97.28
58	9	2	27	4.29	95.28
59	9	3	27	4.32	96.09
60	9	4	32	4.48	97.15
61	9	5	30	4.33	94.53
62	9	6	28	4.34	95.23
63	9	7	29	4.35	96.92
64	10	1	34	4.06	91.48
65	10	2	34	4.17	90.58
66	10	3	35	4.25	93.27
67	10	4	34	4.24	92.89
68	10	5	37	4.30	91.60
69	10	6	35	4.34	90.89
70	10	7	34	4.24	92.69
71	11	1	20	4.21	81.09
72	11	2	22	4.02	81.63
73	11	3	18	4.18	86.63
74	11	4	23	4.24	83.20
75	11	5	23	4.24	83.36
76	11	6	19	4.23	83.22
77	11	7	20	4.33	86.13
78	12	1	31	3.83	92.04
79	12	2	33	3.80	89.07
80	12	3	31	3.78	88.86
81	12	4	32	3.76	90.26
82	12	5	34	3.82	90.65
83	12	6	35	3.78	89.06
84	12	7	35	3.76	93.77
85	13	1	27	3.70	92.81
86	13	2	28	3.71	91.93
87	13	3	25	3.61	91.68
88	13	4	28	3.60	93.13
89	13	5	26	3.71	94.09
90	13	6	30	3.68	89.56
91	13	7	30	3.71	95.37
92	14	1	31	4.09	80.60
93	14	2	31	3.94	77.78
94	14	3	30	4.02	78.80
95	14	4	28	4.13	81.51
96	14	5	29	4.01	79.59
97	14	6	32	4.06	78.94
98	14	7	32	4.06	82.91
99	15	1	31	4.46	86.54
100	15	2	34	4.37	87.59
101	15	3	35	4.34	86.36
102	15	4	33	4.40	84.43
103	15	5	32	4.55	86.95
104	15	6	32	4.56	84.54
105	15	7	35	4.43	85.38
106	16	1	35	3.90	85.08
107	16	2	33	3.97	89.99
108	16	3	31	3.97	88.75
109	16	4	32	3.98	90.80
110	16	5	32	4.05	87.13
111	16	6	34	4.10	88.68
112	16	7	37	4.04	86.66
113	17	1	29	4.18	97.35
114	17	2	31	4.19	94.34
115	17	3	31	4.13	96.65
116	17	4	32	4.27	97.92
117	17	5	33	4.16	94.94
118	17	6	33	4.14	98.32
119	17	7	33	4.29	96.58
120	18	1	36	4.04	76.38
121	18	2	36	4.12	76.52
122	18	3	34	4.07	76.76
123	18	4	35	4.21	79.02
124	18	5	34	4.16	78.27
125	18	6	35	4.28	80.32
126	18	7	34	4.13	80.70
127	19	1	26	4.27	93.02
128	19	2	25	4.35	92.05
129	19	3	26	4.43	95.41
130	19	4	28	4.35	93.17
131	19	5	26	4.26	93.32
132	19	6	25	4.27	94.58
133	19	7	27	4.32	95.00
134	20	1	36	4.38	81.52
135	20	2	35	4.50	80.04
136	20	3	32	4.33	78.77
137	20	4	33	4.50	83.40
138	20	5	35	4.36	79.30
139	20	6	36	4.50	82.08
140	20	7	36	4.42	82.80
141	21	1	33	4.09	89.57
142	21	2	30	4.00	85.29
143	21	3	32	3.99	88.32
144	21	4	32	3.98	87.08
145	21	5	34	4.15	88.23
146	21	6	30	4.01	90.81
147	21	7	31	4.07	89.88
148	22	1	24	4.48	82.66
149	22	2	25	4.35	79.40
150	22	3	26	4.35	83.10
151	22	4	26	4.31	81.04
152	22	5	24	4.44	80.59
153	22	6	27	4.39	80.34
154	22	7	28	4.44	82.49
155	23	1	33	4.29	92.22
156	23	2	34	4.27	92.76
157	23	3	32	4.36	92.16
158	23	4	35	4.38	92.34
159	23	5	34	4.24	91.10
160	23	6	32	4.21	92.73
161	23	7	33	4.39	95.45
162	24	1	28	4.11	89.35
163	24	2	24	4.23	93.23
164	24	3	24	4.14	88.91
165	24	4	29	4.25	88.71
166	24	5	26	4.25	89.88
167	24	6	28	4.12	92.63
168	24	7	28	4.19	92.76
169	25	1	29	4.12	89.88
170	25	2	26	4.14	91.17
171	25	3	26	4.19	88.03
172	25	4	30	4.05	91.54
173	25	5	26	4.12	89.64
174	25	6	27	4.11	93.92
175	25	7	29	4.12	89.45
176	26	1	31	4.38	86.31
177	26	2	34	4.38	85.47
178	26	3	35	4.47	84.64
179	26	4	36	4.35	86.39
180	26	5	35	4.45	85.88
181	26	6	34	4.34	86.78
182	26	7	36	4.33	84.60
183	27	1	26	3.95	84.03
184	27	2	24	3.84	80.31
185	27	3	26	3.83	85.34
186	27	4	26	3.96	81.94
187	27	5	24	3.88	85.01
188	27	6	26	3.90	82.29
189	27	7	27	4.04	84.40
190	28	1	19	3.78	96.69
191	28	2	20	3.86	94.53
192	28	3	20	3.68	96.86
193	28	4	19	3.70	92.25
194	28	5	22	3.86	92.77
195	28	6	19	3.87	93.51
196	28	7	22	3.74	98.50
197	29	1	32	4.27	93.88
198	29	2	30	4.34	94.75
199	29	3	32	4.44	95.21
200	29	4	32	4.29	93.45
201	29	5	32	4.52	95.62
202	29	6	35	4.46	93.47
203	29	7	36	4.40	95.01
204	30	1	27	4.42	81.76
205	30	2	31	4.53	85.66
206	30	3	29	4.42	80.77
207	30	4	28	4.39	86.12
208	30	5	32	4.42	85.68
209	30	6	32	4.64	84.86
210	30	7	33	4.43	86.87
211	31	1	32	3.91	91.15
212	31	2	32	4.05	90.63
213	31	3	31	4.12	89.83
214	31	4	36	4.08	94.10
215	31	5	34	4.15	91.84
216	31	6	35	4.06	94.60
217	31	7	36	4.19	93.00
218	32	1	35	4.41	86.92
219	32	2	31	4.34	88.92
220	32	3	34	4.29	86.32
221	32	4	35	4.41	88.84
222	32	5	32	4.41	87.55
223	32	6	32	4.43	91.25
224	32	7	35	4.39	89.97
225	33	1	19	4.41	85.88
226	33	2	21	4.25	84.61
227	33	3	21	4.31	84.48
228	33	4	22	4.38	82.90
229	33	5	18	4.44	84.64
230	33	6	18	4.52	87.03
231	33	7	22	4.44	82.53
232	34	1	20	3.89	92.41
233	34	2	20	4.02	93.67
234	34	3	19	3.98	94.12
235	34	4	20	3.99	93.85
236	34	5	24	3.98	91.78
237	34	6	20	4.06	94.69
238	34	7	24	4.20	92.79
239	35	1	32	3.94	97.01
240	35	2	33	3.89	97.72
241	35	3	32	3.82	93.21
242	35	4	33	3.84	92.54
243	35	5	37	3.95	95.62
244	35	6	35	3.83	97.30
245	35	7	38	3.87	97.21
246	36	1	25	4.48	93.14
247	36	2	21	4.50	91.83
248	36	3	24	4.50	92.22
249	36	4	22	4.51	94.40
250	36	5	25	4.59	92.43
251	36	6	23	4.49	92.86
252	36	7	25	4.57	97.87
253	37	1	32	4.44	86.79
254	37	2	31	4.53	87.76
255	37	3	35	4.57	91.95
256	37	4	35	4.60	88.47
257	37	5	34	4.45	91.17
258	37	6	33	4.43	90.45
259	37	7	36	4.60	92.50
260	38	1	33	3.94	80.64
261	38	2	35	3.84	80.32
262	38	3	31	3.94	80.57
263	38	4	34	4.02	82.86
264	38	5	36	3.94	84.18
265	38	6	32	4.15	82.06
266	38	7	34	4.10	83.84
267	39	1	30	3.77	96.00
268	39	2	30	3.78	94.81
269	39	3	32	3.68	92.86
270	39	4	34	3.80	93.28
271	39	5	32	3.70	96.35
272	39	6	31	3.80	96.75
273	39	7	34	3.87	93.87
274	40	1	20	3.59	85.86
275	40	2	21	3.73	88.38
276	40	3	21	3.69	91.04
277	40	4	21	3.65	90.08
278	40	5	22	3.63	88.53
279	40	6	20	3.60	90.24
280	40	7	21	3.65	91.45
\.


--
-- Data for Name: indicator_values; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.indicator_values (id, indicator_id, period_id, faculty_id, value, updated_at) FROM stdin;
1	1	1	1	357.00	2026-11-23 23:08:57.542956
2	2	1	1	262.00	2026-11-23 23:08:57.542956
3	3	1	1	95.00	2026-11-23 23:08:57.542956
4	4	1	1	90.00	2026-11-23 23:08:57.542956
5	5	1	1	14.00	2026-11-23 23:08:57.542956
6	6	1	1	0.00	2026-11-23 23:08:57.542956
7	7	1	1	4.10	2026-11-23 23:08:57.542956
8	8	1	1	89.33	2026-11-23 23:08:57.542956
9	9	1	1	32.00	2026-11-23 23:08:57.542956
10	10	1	1	64.00	2026-11-23 23:08:57.542956
11	11	1	1	21152.00	2026-11-23 23:08:57.542956
12	12	1	1	46.00	2026-11-23 23:08:57.542956
13	1	1	2	452.00	2026-11-23 23:08:57.542956
14	2	1	2	297.00	2026-11-23 23:08:57.542956
15	3	1	2	155.00	2026-11-23 23:08:57.542956
16	4	1	2	112.00	2026-11-23 23:08:57.542956
17	5	1	2	13.00	2026-11-23 23:08:57.542956
18	6	1	2	0.00	2026-11-23 23:08:57.542956
19	7	1	2	4.15	2026-11-23 23:08:57.542956
20	8	1	2	87.28	2026-11-23 23:08:57.542956
21	9	1	2	48.00	2026-11-23 23:08:57.542956
22	10	1	2	53.00	2026-11-23 23:08:57.542956
23	11	1	2	34080.00	2026-11-23 23:08:57.542956
24	12	1	2	50.00	2026-11-23 23:08:57.542956
25	1	1	3	77.00	2026-11-23 23:08:57.542956
26	2	1	3	54.00	2026-11-23 23:08:57.542956
27	3	1	3	23.00	2026-11-23 23:08:57.542956
28	4	1	3	21.00	2026-11-23 23:08:57.542956
29	5	1	3	2.00	2026-11-23 23:08:57.542956
30	6	1	3	0.00	2026-11-23 23:08:57.542956
31	7	1	3	4.04	2026-11-23 23:08:57.542956
32	8	1	3	91.25	2026-11-23 23:08:57.542956
33	9	1	3	12.00	2026-11-23 23:08:57.542956
34	10	1	3	70.10	2026-11-23 23:08:57.542956
35	11	1	3	8052.00	2026-11-23 23:08:57.542956
36	12	1	3	11.00	2026-11-23 23:08:57.542956
37	1	1	4	113.00	2026-11-23 23:08:57.542956
38	2	1	4	76.00	2026-11-23 23:08:57.542956
39	3	1	4	37.00	2026-11-23 23:08:57.542956
40	4	1	4	32.00	2026-11-23 23:08:57.542956
41	5	1	4	2.00	2026-11-23 23:08:57.542956
42	6	1	4	0.00	2026-11-23 23:08:57.542956
43	7	1	4	4.27	2026-11-23 23:08:57.542956
44	8	1	4	86.71	2026-11-23 23:08:57.542956
45	9	1	4	12.00	2026-11-23 23:08:57.542956
46	10	1	4	68.30	2026-11-23 23:08:57.542956
47	11	1	4	8700.00	2026-11-23 23:08:57.542956
48	12	1	4	15.00	2026-11-23 23:08:57.542956
49	1	1	5	142.00	2026-11-23 23:08:57.542956
50	2	1	5	98.00	2026-11-23 23:08:57.542956
51	3	1	5	44.00	2026-11-23 23:08:57.542956
52	4	1	5	37.00	2026-11-23 23:08:57.542956
53	5	1	5	2.00	2026-11-23 23:08:57.542956
54	6	1	5	0.00	2026-11-23 23:08:57.542956
55	7	1	5	4.14	2026-11-23 23:08:57.542956
56	8	1	5	89.57	2026-11-23 23:08:57.542956
57	9	1	5	14.00	2026-11-23 23:08:57.542956
58	10	1	5	55.40	2026-11-23 23:08:57.542956
59	11	1	5	9016.00	2026-11-23 23:08:57.542956
60	12	1	5	20.00	2026-11-23 23:08:57.542956
61	1	2	1	348.00	2026-11-23 23:08:57.542956
62	2	2	1	244.00	2026-11-23 23:08:57.542956
63	3	2	1	104.00	2026-11-23 23:08:57.542956
64	4	2	1	0.00	2026-11-23 23:08:57.542956
65	5	2	1	14.00	2026-11-23 23:08:57.542956
66	6	2	1	67.00	2026-11-23 23:08:57.542956
67	7	2	1	4.09	2026-11-23 23:08:57.542956
68	8	2	1	88.93	2026-11-23 23:08:57.542956
69	9	2	1	33.00	2026-11-23 23:08:57.542956
70	10	2	1	65.20	2026-11-23 23:08:57.542956
71	11	2	1	24816.00	2026-11-23 23:08:57.542956
72	12	2	1	41.00	2026-11-23 23:08:57.542956
73	1	2	2	449.00	2026-11-23 23:08:57.542956
74	2	2	2	338.00	2026-11-23 23:08:57.542956
75	3	2	2	111.00	2026-11-23 23:08:57.542956
76	4	2	2	0.00	2026-11-23 23:08:57.542956
77	5	2	2	9.00	2026-11-23 23:08:57.542956
78	6	2	2	99.00	2026-11-23 23:08:57.542956
79	7	2	2	4.16	2026-11-23 23:08:57.542956
80	8	2	2	86.98	2026-11-23 23:08:57.542956
81	9	2	2	38.00	2026-11-23 23:08:57.542956
82	10	2	2	71.60	2026-11-23 23:08:57.542956
83	11	2	2	26752.00	2026-11-23 23:08:57.542956
84	12	2	2	41.00	2026-11-23 23:08:57.542956
85	1	2	3	74.00	2026-11-23 23:08:57.542956
86	2	2	3	58.00	2026-11-23 23:08:57.542956
87	3	2	3	16.00	2026-11-23 23:08:57.542956
88	4	2	3	0.00	2026-11-23 23:08:57.542956
89	5	2	3	2.00	2026-11-23 23:08:57.542956
90	6	2	3	13.00	2026-11-23 23:08:57.542956
91	7	2	3	4.05	2026-11-23 23:08:57.542956
92	8	2	3	90.01	2026-11-23 23:08:57.542956
93	9	2	3	12.00	2026-11-23 23:08:57.542956
94	10	2	3	61.20	2026-11-23 23:08:57.542956
95	11	2	3	8268.00	2026-11-23 23:08:57.542956
96	12	2	3	16.00	2026-11-23 23:08:57.542956
97	1	2	4	115.00	2026-11-23 23:08:57.542956
98	2	2	4	88.00	2026-11-23 23:08:57.542956
99	3	2	4	27.00	2026-11-23 23:08:57.542956
100	4	2	4	0.00	2026-11-23 23:08:57.542956
101	5	2	4	4.00	2026-11-23 23:08:57.542956
102	6	2	4	25.00	2026-11-23 23:08:57.542956
103	7	2	4	4.29	2026-11-23 23:08:57.542956
104	8	2	4	87.73	2026-11-23 23:08:57.542956
105	9	2	4	12.00	2026-11-23 23:08:57.542956
106	10	2	4	57.70	2026-11-23 23:08:57.542956
107	11	2	4	9000.00	2026-11-23 23:08:57.542956
108	12	2	4	17.00	2026-11-23 23:08:57.542956
109	1	2	5	140.00	2026-11-23 23:08:57.542956
110	2	2	5	106.00	2026-11-23 23:08:57.542956
111	3	2	5	34.00	2026-11-23 23:08:57.542956
112	4	2	5	0.00	2026-11-23 23:08:57.542956
113	5	2	5	2.00	2026-11-23 23:08:57.542956
114	6	2	5	29.00	2026-11-23 23:08:57.542956
115	7	2	5	4.13	2026-11-23 23:08:57.542956
116	8	2	5	89.70	2026-11-23 23:08:57.542956
117	9	2	5	15.00	2026-11-23 23:08:57.542956
118	10	2	5	58.00	2026-11-23 23:08:57.542956
119	11	2	5	11160.00	2026-11-23 23:08:57.542956
120	12	2	5	14.00	2026-11-23 23:08:57.542956
121	1	3	1	349.00	2026-11-23 23:08:57.542956
122	2	3	1	245.00	2026-11-23 23:08:57.542956
123	3	3	1	104.00	2026-11-23 23:08:57.542956
124	4	3	1	92.00	2026-11-23 23:08:57.542956
125	5	3	1	15.00	2026-11-23 23:08:57.542956
126	6	3	1	0.00	2026-11-23 23:08:57.542956
127	7	3	1	4.12	2026-11-23 23:08:57.542956
128	8	3	1	90.39	2026-11-23 23:08:57.542956
129	9	3	1	34.00	2026-11-23 23:08:57.542956
130	10	3	1	52.00	2026-11-23 23:08:57.542956
131	11	3	1	23460.00	2026-11-23 23:08:57.542956
132	12	3	1	31.00	2026-11-23 23:08:57.542956
133	1	3	2	447.00	2026-11-23 23:08:57.542956
134	2	3	2	320.00	2026-11-23 23:08:57.542956
135	3	3	2	127.00	2026-11-23 23:08:57.542956
136	4	3	2	134.00	2026-11-23 23:08:57.542956
137	5	3	2	14.00	2026-11-23 23:08:57.542956
138	6	3	2	0.00	2026-11-23 23:08:57.542956
139	7	3	2	4.15	2026-11-23 23:08:57.542956
140	8	3	2	87.14	2026-11-23 23:08:57.542956
141	9	3	2	41.00	2026-11-23 23:08:57.542956
142	10	3	2	59.20	2026-11-23 23:08:57.542956
143	11	3	2	27921.00	2026-11-23 23:08:57.542956
144	12	3	2	43.00	2026-11-23 23:08:57.542956
145	1	3	3	78.00	2026-11-23 23:08:57.542956
146	2	3	3	48.00	2026-11-23 23:08:57.542956
147	3	3	3	30.00	2026-11-23 23:08:57.542956
148	4	3	3	22.00	2026-11-23 23:08:57.542956
149	5	3	3	3.00	2026-11-23 23:08:57.542956
150	6	3	3	0.00	2026-11-23 23:08:57.542956
151	7	3	3	4.04	2026-11-23 23:08:57.542956
152	8	3	3	92.34	2026-11-23 23:08:57.542956
153	9	3	3	12.00	2026-11-23 23:08:57.542956
154	10	3	3	60.30	2026-11-23 23:08:57.542956
155	11	3	3	8304.00	2026-11-23 23:08:57.542956
156	12	3	3	11.00	2026-11-23 23:08:57.542956
157	1	3	4	115.00	2026-11-23 23:08:57.542956
158	2	3	4	73.00	2026-11-23 23:08:57.542956
159	3	3	4	42.00	2026-11-23 23:08:57.542956
160	4	3	4	33.00	2026-11-23 23:08:57.542956
161	5	3	4	3.00	2026-11-23 23:08:57.542956
162	6	3	4	0.00	2026-11-23 23:08:57.542956
163	7	3	4	4.28	2026-11-23 23:08:57.542956
164	8	3	4	85.53	2026-11-23 23:08:57.542956
165	9	3	4	12.00	2026-11-23 23:08:57.542956
166	10	3	4	60.90	2026-11-23 23:08:57.542956
167	11	3	4	8592.00	2026-11-23 23:08:57.542956
168	12	3	4	11.00	2026-11-23 23:08:57.542956
169	1	3	5	141.00	2026-11-23 23:08:57.542956
170	2	3	5	89.00	2026-11-23 23:08:57.542956
171	3	3	5	52.00	2026-11-23 23:08:57.542956
172	4	3	5	36.00	2026-11-23 23:08:57.542956
173	5	3	5	6.00	2026-11-23 23:08:57.542956
174	6	3	5	0.00	2026-11-23 23:08:57.542956
175	7	3	5	4.17	2026-11-23 23:08:57.542956
176	8	3	5	90.07	2026-11-23 23:08:57.542956
177	9	3	5	15.00	2026-11-23 23:08:57.542956
178	10	3	5	71.20	2026-11-23 23:08:57.542956
179	11	3	5	11355.00	2026-11-23 23:08:57.542956
180	12	3	5	24.00	2026-11-23 23:08:57.542956
181	1	4	1	377.00	2026-11-23 23:08:57.542956
182	2	4	1	282.00	2026-11-23 23:08:57.542956
183	3	4	1	95.00	2026-11-23 23:08:57.542956
184	4	4	1	0.00	2026-11-23 23:08:57.542956
185	5	4	1	16.00	2026-11-23 23:08:57.542956
186	6	4	1	70.00	2026-11-23 23:08:57.542956
187	7	4	1	4.13	2026-11-23 23:08:57.542956
188	8	4	1	90.42	2026-11-23 23:08:57.542956
189	9	4	1	37.00	2026-11-23 23:08:57.542956
190	10	4	1	66.30	2026-11-23 23:08:57.542956
191	11	4	1	25678.00	2026-11-23 23:08:57.542956
192	12	4	1	56.00	2026-11-23 23:08:57.542956
193	1	4	2	464.00	2026-11-23 23:08:57.542956
194	2	4	2	292.00	2026-11-23 23:08:57.542956
195	3	4	2	172.00	2026-11-23 23:08:57.542956
196	4	4	2	0.00	2026-11-23 23:08:57.542956
197	5	4	2	12.00	2026-11-23 23:08:57.542956
198	6	4	2	93.00	2026-11-23 23:08:57.542956
199	7	4	2	4.19	2026-11-23 23:08:57.542956
200	8	4	2	88.04	2026-11-23 23:08:57.542956
201	9	4	2	44.00	2026-11-23 23:08:57.542956
202	10	4	2	52.20	2026-11-23 23:08:57.542956
203	11	4	2	28424.00	2026-11-23 23:08:57.542956
204	12	4	2	50.00	2026-11-23 23:08:57.542956
205	1	4	3	77.00	2026-11-23 23:08:57.542956
206	2	4	3	53.00	2026-11-23 23:08:57.542956
207	3	4	3	24.00	2026-11-23 23:08:57.542956
208	4	4	3	0.00	2026-11-23 23:08:57.542956
209	5	4	3	3.00	2026-11-23 23:08:57.542956
210	6	4	3	16.00	2026-11-23 23:08:57.542956
211	7	4	3	4.03	2026-11-23 23:08:57.542956
212	8	4	3	89.27	2026-11-23 23:08:57.542956
213	9	4	3	12.00	2026-11-23 23:08:57.542956
214	10	4	3	60.00	2026-11-23 23:08:57.542956
215	11	4	3	8208.00	2026-11-23 23:08:57.542956
216	12	4	3	19.00	2026-11-23 23:08:57.542956
217	1	4	4	121.00	2026-11-23 23:08:57.542956
218	2	4	4	75.00	2026-11-23 23:08:57.542956
219	3	4	4	46.00	2026-11-23 23:08:57.542956
220	4	4	4	0.00	2026-11-23 23:08:57.542956
221	5	4	4	4.00	2026-11-23 23:08:57.542956
222	6	4	4	24.00	2026-11-23 23:08:57.542956
223	7	4	4	4.30	2026-11-23 23:08:57.542956
224	8	4	4	88.70	2026-11-23 23:08:57.542956
225	9	4	4	13.00	2026-11-23 23:08:57.542956
226	10	4	4	68.40	2026-11-23 23:08:57.542956
227	11	4	4	9035.00	2026-11-23 23:08:57.542956
228	12	4	4	19.00	2026-11-23 23:08:57.542956
229	1	4	5	144.00	2026-11-23 23:08:57.542956
230	2	4	5	105.00	2026-11-23 23:08:57.542956
231	3	4	5	39.00	2026-11-23 23:08:57.542956
232	4	4	5	0.00	2026-11-23 23:08:57.542956
233	5	4	5	5.00	2026-11-23 23:08:57.542956
234	6	4	5	29.00	2026-11-23 23:08:57.542956
235	7	4	5	4.19	2026-11-23 23:08:57.542956
236	8	4	5	89.73	2026-11-23 23:08:57.542956
237	9	4	5	14.00	2026-11-23 23:08:57.542956
238	10	4	5	65.00	2026-11-23 23:08:57.542956
239	11	4	5	9982.00	2026-11-23 23:08:57.542956
240	12	4	5	20.00	2026-11-23 23:08:57.542956
241	1	5	1	376.00	2026-11-23 23:08:57.542956
242	2	5	1	249.00	2026-11-23 23:08:57.542956
243	3	5	1	127.00	2026-11-23 23:08:57.542956
244	4	5	1	101.00	2026-11-23 23:08:57.542956
245	5	5	1	11.00	2026-11-23 23:08:57.542956
246	6	5	1	0.00	2026-11-23 23:08:57.542956
247	7	5	1	4.15	2026-11-23 23:08:57.542956
248	8	5	1	90.04	2026-11-23 23:08:57.542956
249	9	5	1	37.00	2026-11-23 23:08:57.542956
250	10	5	1	56.00	2026-11-23 23:08:57.542956
251	11	5	1	27565.00	2026-11-23 23:08:57.542956
252	12	5	1	48.00	2026-11-23 23:08:57.542956
253	1	5	2	454.00	2026-11-23 23:08:57.542956
254	2	5	2	295.00	2026-11-23 23:08:57.542956
255	3	5	2	159.00	2026-11-23 23:08:57.542956
256	4	5	2	101.00	2026-11-23 23:08:57.542956
257	5	5	2	14.00	2026-11-23 23:08:57.542956
258	6	5	2	0.00	2026-11-23 23:08:57.542956
259	7	5	2	4.18	2026-11-23 23:08:57.542956
260	8	5	2	87.25	2026-11-23 23:08:57.542956
261	9	5	2	44.00	2026-11-23 23:08:57.542956
262	10	5	2	63.10	2026-11-23 23:08:57.542956
263	11	5	2	29788.00	2026-11-23 23:08:57.542956
264	12	5	2	50.00	2026-11-23 23:08:57.542956
265	1	5	3	78.00	2026-11-23 23:08:57.542956
266	2	5	3	59.00	2026-11-23 23:08:57.542956
267	3	5	3	19.00	2026-11-23 23:08:57.542956
268	4	5	3	22.00	2026-11-23 23:08:57.542956
269	5	5	3	3.00	2026-11-23 23:08:57.542956
270	6	5	3	0.00	2026-11-23 23:08:57.542956
271	7	5	3	4.14	2026-11-23 23:08:57.542956
272	8	5	3	91.55	2026-11-23 23:08:57.542956
273	9	5	3	12.00	2026-11-23 23:08:57.542956
274	10	5	3	64.60	2026-11-23 23:08:57.542956
275	11	5	3	7920.00	2026-11-23 23:08:57.542956
276	12	5	3	13.00	2026-11-23 23:08:57.542956
277	1	5	4	116.00	2026-11-23 23:08:57.542956
278	2	5	4	82.00	2026-11-23 23:08:57.542956
279	3	5	4	34.00	2026-11-23 23:08:57.542956
280	4	5	4	28.00	2026-11-23 23:08:57.542956
281	5	5	4	5.00	2026-11-23 23:08:57.542956
282	6	5	4	0.00	2026-11-23 23:08:57.542956
283	7	5	4	4.34	2026-11-23 23:08:57.542956
284	8	5	4	87.84	2026-11-23 23:08:57.542956
285	9	5	4	12.00	2026-11-23 23:08:57.542956
286	10	5	4	56.30	2026-11-23 23:08:57.542956
287	11	5	4	9084.00	2026-11-23 23:08:57.542956
288	12	5	4	12.00	2026-11-23 23:08:57.542956
289	1	5	5	156.00	2026-11-23 23:08:57.542956
290	2	5	5	112.00	2026-11-23 23:08:57.542956
291	3	5	5	44.00	2026-11-23 23:08:57.542956
292	4	5	5	43.00	2026-11-23 23:08:57.542956
293	5	5	5	7.00	2026-11-23 23:08:57.542956
294	6	5	5	0.00	2026-11-23 23:08:57.542956
295	7	5	5	4.16	2026-11-23 23:08:57.542956
296	8	5	5	90.91	2026-11-23 23:08:57.542956
297	9	5	5	14.00	2026-11-23 23:08:57.542956
298	10	5	5	53.30	2026-11-23 23:08:57.542956
299	11	5	5	9562.00	2026-11-23 23:08:57.542956
300	12	5	5	16.00	2026-11-23 23:08:57.542956
301	1	6	1	373.00	2026-11-23 23:08:57.542956
302	2	6	1	257.00	2026-11-23 23:08:57.542956
303	3	6	1	116.00	2026-11-23 23:08:57.542956
304	4	6	1	0.00	2026-11-23 23:08:57.542956
305	5	6	1	9.00	2026-11-23 23:08:57.542956
306	6	6	1	70.00	2026-11-23 23:08:57.542956
307	7	6	1	4.18	2026-11-23 23:08:57.542956
308	8	6	1	89.85	2026-11-23 23:08:57.542956
309	9	6	1	36.00	2026-11-23 23:08:57.542956
310	10	6	1	59.90	2026-11-23 23:08:57.542956
311	11	6	1	26820.00	2026-11-23 23:08:57.542956
312	12	6	1	57.00	2026-11-23 23:08:57.542956
313	1	6	2	456.00	2026-11-23 23:08:57.542956
314	2	6	2	338.00	2026-11-23 23:08:57.542956
315	3	6	2	118.00	2026-11-23 23:08:57.542956
316	4	6	2	0.00	2026-11-23 23:08:57.542956
317	5	6	2	10.00	2026-11-23 23:08:57.542956
318	6	6	2	92.00	2026-11-23 23:08:57.542956
319	7	6	2	4.18	2026-11-23 23:08:57.542956
320	8	6	2	88.52	2026-11-23 23:08:57.542956
321	9	6	2	44.00	2026-11-23 23:08:57.542956
322	10	6	2	51.30	2026-11-23 23:08:57.542956
323	11	6	2	30140.00	2026-11-23 23:08:57.542956
324	12	6	2	49.00	2026-11-23 23:08:57.542956
325	1	6	3	80.00	2026-11-23 23:08:57.542956
326	2	6	3	54.00	2026-11-23 23:08:57.542956
327	3	6	3	26.00	2026-11-23 23:08:57.542956
328	4	6	3	0.00	2026-11-23 23:08:57.542956
329	5	6	3	2.00	2026-11-23 23:08:57.542956
330	6	6	3	16.00	2026-11-23 23:08:57.542956
331	7	6	3	4.14	2026-11-23 23:08:57.542956
332	8	6	3	89.85	2026-11-23 23:08:57.542956
333	9	6	3	12.00	2026-11-23 23:08:57.542956
334	10	6	3	62.20	2026-11-23 23:08:57.542956
335	11	6	3	8604.00	2026-11-23 23:08:57.542956
336	12	6	3	10.00	2026-11-23 23:08:57.542956
337	1	6	4	117.00	2026-11-23 23:08:57.542956
338	2	6	4	86.00	2026-11-23 23:08:57.542956
339	3	6	4	31.00	2026-11-23 23:08:57.542956
340	4	6	4	0.00	2026-11-23 23:08:57.542956
341	5	6	4	3.00	2026-11-23 23:08:57.542956
342	6	6	4	21.00	2026-11-23 23:08:57.542956
343	7	6	4	4.39	2026-11-23 23:08:57.542956
344	8	6	4	89.86	2026-11-23 23:08:57.542956
345	9	6	4	12.00	2026-11-23 23:08:57.542956
346	10	6	4	69.50	2026-11-23 23:08:57.542956
347	11	6	4	8340.00	2026-11-23 23:08:57.542956
348	12	6	4	12.00	2026-11-23 23:08:57.542956
349	1	6	5	143.00	2026-11-23 23:08:57.542956
350	2	6	5	96.00	2026-11-23 23:08:57.542956
351	3	6	5	47.00	2026-11-23 23:08:57.542956
352	4	6	5	0.00	2026-11-23 23:08:57.542956
353	5	6	5	5.00	2026-11-23 23:08:57.542956
354	6	6	5	26.00	2026-11-23 23:08:57.542956
355	7	6	5	4.18	2026-11-23 23:08:57.542956
356	8	6	5	91.23	2026-11-23 23:08:57.542956
357	9	6	5	12.00	2026-11-23 23:08:57.542956
358	10	6	5	56.20	2026-11-23 23:08:57.542956
359	11	6	5	7788.00	2026-11-23 23:08:57.542956
360	12	6	5	12.00	2026-11-23 23:08:57.542956
361	1	7	1	380.00	2026-11-23 23:08:57.542956
362	2	7	1	239.00	2026-11-23 23:08:57.542956
363	3	7	1	141.00	2026-11-23 23:08:57.542956
364	4	7	1	110.00	2026-11-23 23:08:57.542956
365	5	7	1	12.00	2026-11-23 23:08:57.542956
366	6	7	1	0.00	2026-11-23 23:08:57.542956
367	7	7	1	4.15	2026-11-23 23:08:57.542956
368	8	7	1	91.24	2026-11-23 23:08:57.542956
369	9	7	1	38.00	2026-11-23 23:08:57.542956
370	10	7	1	62.50	2026-11-23 23:08:57.542956
371	11	7	1	27588.00	2026-11-23 23:08:57.542956
372	12	7	1	49.00	2026-11-23 23:08:57.542956
373	1	7	2	474.00	2026-11-23 23:08:57.542956
374	2	7	2	333.00	2026-11-23 23:08:57.542956
375	3	7	2	141.00	2026-11-23 23:08:57.542956
376	4	7	2	115.00	2026-11-23 23:08:57.542956
377	5	7	2	7.00	2026-11-23 23:08:57.542956
378	6	7	2	0.00	2026-11-23 23:08:57.542956
379	7	7	2	4.20	2026-11-23 23:08:57.542956
380	8	7	2	88.44	2026-11-23 23:08:57.542956
381	9	7	2	44.00	2026-11-23 23:08:57.542956
382	10	7	2	61.60	2026-11-23 23:08:57.542956
383	11	7	2	28776.00	2026-11-23 23:08:57.542956
384	12	7	2	60.00	2026-11-23 23:08:57.542956
385	1	7	3	85.00	2026-11-23 23:08:57.542956
386	2	7	3	54.00	2026-11-23 23:08:57.542956
387	3	7	3	31.00	2026-11-23 23:08:57.542956
388	4	7	3	24.00	2026-11-23 23:08:57.542956
389	5	7	3	4.00	2026-11-23 23:08:57.542956
390	6	7	3	0.00	2026-11-23 23:08:57.542956
391	7	7	3	4.11	2026-11-23 23:08:57.542956
392	8	7	3	92.54	2026-11-23 23:08:57.542956
393	9	7	3	12.00	2026-11-23 23:08:57.542956
394	10	7	3	72.60	2026-11-23 23:08:57.542956
395	11	7	3	8784.00	2026-11-23 23:08:57.542956
396	12	7	3	13.00	2026-11-23 23:08:57.542956
397	1	7	4	126.00	2026-11-23 23:08:57.542956
398	2	7	4	81.00	2026-11-23 23:08:57.542956
399	3	7	4	45.00	2026-11-23 23:08:57.542956
400	4	7	4	33.00	2026-11-23 23:08:57.542956
401	5	7	4	1.00	2026-11-23 23:08:57.542956
402	6	7	4	0.00	2026-11-23 23:08:57.542956
403	7	7	4	4.35	2026-11-23 23:08:57.542956
404	8	7	4	88.72	2026-11-23 23:08:57.542956
405	9	7	4	12.00	2026-11-23 23:08:57.542956
406	10	7	4	70.10	2026-11-23 23:08:57.542956
407	11	7	4	8112.00	2026-11-23 23:08:57.542956
408	12	7	4	14.00	2026-11-23 23:08:57.542956
409	1	7	5	157.00	2026-11-23 23:08:57.542956
410	2	7	5	107.00	2026-11-23 23:08:57.542956
411	3	7	5	50.00	2026-11-23 23:08:57.542956
412	4	7	5	45.00	2026-11-23 23:08:57.542956
413	5	7	5	3.00	2026-11-23 23:08:57.542956
414	6	7	5	0.00	2026-11-23 23:08:57.542956
415	7	7	5	4.25	2026-11-23 23:08:57.542956
416	8	7	5	92.66	2026-11-23 23:08:57.542956
417	9	7	5	14.00	2026-11-23 23:08:57.542956
418	10	7	5	52.80	2026-11-23 23:08:57.542956
419	11	7	5	9506.00	2026-11-23 23:08:57.542956
420	12	7	5	13.00	2026-11-23 23:08:57.542956
\.


--
-- Data for Name: indicators; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.indicators (id, code, name, unit, category, description, is_public) FROM stdin;
1	STUDENTS_TOTAL	Численность студентов	чел.	Контингент	Общее число обучающихся на начало периода	t
2	STUDENTS_FULLTIME	Студенты очной формы	чел.	Контингент	Число обучающихся по очной форме	t
3	STUDENTS_PARTTIME	Студенты заочной и очно-заочной форм	чел.	Контингент	Число обучающихся по заочной и очно-заочной формам	f
4	ADMITTED	Принято на первый курс	чел.	Контингент	Приём на первый курс за период	t
5	EXPELLED	Отчислено студентов	чел.	Контингент	Число отчисленных за период	f
6	GRADUATES	Выпуск	чел.	Контингент	Число выпускников за период	t
7	AVG_GRADE	Средний балл по итогам сессии	балл	Успеваемость	Средневзвешенный балл по студентам факультета	t
8	PASS_RATE	Доля студентов без задолженностей	%	Успеваемость	Доля сдавших сессию в срок	t
9	STAFF_TOTAL	Численность профессорско-преподавательского состава	чел.	Кадры	Штатные и совместители, пересчёт на физические лица	f
10	STAFF_DEGREE	Доля ППС с учёной степенью	%	Кадры	Кандидаты и доктора наук от общего числа ППС	t
11	LOAD_HOURS	Плановая учебная нагрузка	час.	Нагрузка	Суммарная плановая нагрузка кафедр факультета	f
12	PUBLICATIONS	Научные публикации	шт.	Наука	Публикации ППС в РИНЦ за период	f
\.


--
-- Data for Name: integration_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.integration_settings (key, value, updated_at) FROM stdin;
onec_url		2026-11-23 23:08:57.542956
onec_login	stat_reader	2026-11-23 23:08:57.542956
sync_interval_minutes	60	2026-11-23 23:08:57.542956
onec_base	UniversityStat	2026-11-23 23:08:57.542956
\.


--
-- Data for Name: news; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.news (id, title, summary, body, published_at, author_id, is_published) FROM stdin;
1	Запущена пробная версия модуля визуализации данных	Кафедра информационных систем начала опытную эксплуатацию модуля Витте-Дашборд.	Модуль подключается к единому центру статистических данных и строит интерактивные дашборды без ручной выгрузки в Excel. Опытная эксплуатация продлится пять рабочих дней.	2026-11-23 23:08:57.542956	1	t
2	Дашборд «Ключевые показатели» доступен руководству	Ректорат получил сводную панель из пяти ключевых показателей.	На панели отображаются численность студентов, динамика среднего балла, доля студентов без задолженностей, доля преподавателей со степенью и приём на первый курс.	2026-11-20 23:08:57.542956	1	t
3	Экспорт отчётов в Word и Excel	Сотрудники УМУ могут выгружать отчёты в форматах DOCX и XLSX.	В разделе «Отчёты» выбирается тип отчёта, период и факультет. История выгрузок сохраняется в личном кабинете пользователя.	2026-11-17 23:08:57.542956	1	t
4	Автоматическая синхронизация с 1С:Предприятие	Данные обновляются по кнопке «Обновить» и по расписанию — раз в час.	Администратор настраивает адрес HTTP-сервиса 1С в панели администратора и контролирует журнал синхронизации.	2026-11-14 23:08:57.542956	1	t
5	Разграничение прав доступа по ролям	В системе работают четыре роли: администратор, руководство, УМУ и деканат.	Деканат видит данные только своего факультета, руководство — все дашборды, а администратор управляет пользователями и справочниками.	2026-11-11 23:08:57.542956	1	t
6	Инструктаж для пользователей модуля	Для сотрудников УМУ пройдёт двухчасовой инструктаж.	Участникам будет выдано краткое руководство пользователя. Запись на инструктаж — через форму обратной связи.	2026-11-08 23:08:57.542956	1	t
\.


--
-- Data for Name: report_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.report_history (id, user_id, report_type, params, file_format, file_name, created_at) FROM stdin;
1	3	performance	{"period": 5, "faculty": "all"}	xlsx	performance_example.xlsx	2026-11-23 23:08:57.542956
2	2	contingent	{"period": 7, "faculty": "all"}	docx	contingent_example.docx	2026-11-23 23:08:57.542956
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roles (id, code, name, description, level) FROM stdin;
1	admin	Администратор	Полный доступ, управление пользователями и интеграцией	4
2	leadership	Руководство	Просмотр всех дашбордов и выгрузка отчётов	3
3	umu	УМУ	Формирование отчётов учебно-методического управления	2
4	dean	Деканат	Просмотр данных своего факультета	1
\.


--
-- Data for Name: study_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.study_groups (id, direction_id, name, course, study_form) FROM stdin;
1	1	ПИ-251	1	Очная
2	1	ПИ-241	2	Очная
3	1	ПИ-231	3	Очная
4	1	ПИ-221	4	Очная
5	1	ПИ-23З	3	Заочная
6	2	ИВТ-251	1	Очная
7	2	ИВТ-241	2	Очная
8	2	ИВТ-231	3	Очная
9	2	ИВТ-221	4	Очная
10	3	ИБ-251	1	Очная
11	3	ИБ-241	2	Очная
12	3	ИБ-231	3	Очная
13	3	ИБ-221	4	Очная
14	4	ЭК-251	1	Очная
15	4	ЭК-241	2	Очная
16	4	ЭК-231	3	Очная
17	4	ЭК-221	4	Очная
18	4	ЭК-23З	3	Заочная
19	5	МН-251	1	Очная
20	5	МН-241	2	Очная
21	5	МН-231	3	Очная
22	5	МН-221	4	Очная
23	6	ГМУ-251	1	Очная
24	6	ГМУ-241	2	Очная
25	6	ГМУ-231	3	Очная
26	6	ГМУ-221	4	Очная
27	7	ЮР-251	1	Очная
28	7	ЮР-231	3	Очная
29	7	ЮР-23З	3	Заочная
30	8	ПС-251	1	Очная
31	8	ПС-231	3	Очная
32	9	ППО-251	1	Очная
33	9	ППО-231	3	Очная
34	10	РСО-251	1	Очная
35	10	РСО-231	3	Очная
36	10	РСО-23З	3	Заочная
37	11	ДЗ-251	1	Очная
38	11	ДЗ-231	3	Очная
39	12	БИ-251	1	Очная
40	12	БИ-231	3	Очная
\.


--
-- Data for Name: sync_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sync_log (id, started_at, finished_at, source, status, rows_loaded, message, started_by) FROM stdin;
1	2026-11-23 22:08:57.542956	2026-11-23 22:09:01.542956	onec-file	ok	420	Тестовая загрузка завершена	1
2	2026-11-22 22:08:57.542956	2026-11-22 22:09:01.542956	onec-file	ok	420	Тестовая загрузка завершена	1
3	2026-11-21 22:08:57.542956	2026-11-21 22:09:01.542956	onec-file	ok	420	Тестовая загрузка завершена	1
\.


--
-- Data for Name: uploaded_files; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.uploaded_files (id, user_id, original_name, stored_name, size_bytes, uploaded_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, login, password_hash, full_name, email, role_id, faculty_id, is_active, preferences, created_at, last_login) FROM stdin;
1	admin	pbkdf2:sha256:1000000$TUKERoy8lCoa5H24$31b5fa1f21b42305b87313547fa36b3b5fff8e77bc29f213961b47d9f0ce6bd9	Новоселов Антон Андреевич	admin@vitte.local	1	\N	t	{}	2026-11-23 23:08:57.542956	\N
3	umu	pbkdf2:sha256:1000000$JNIiIrgQpXiMSvKb$1fc0c273c5bc0287d11fdaa2287f9883cbd6d4a1daa7ede682bca55264e02a2d	Иванова Светлана Михайловна	umu@vitte.local	3	\N	t	{}	2026-11-23 23:08:57.542956	\N
4	dean_fit	pbkdf2:sha256:1000000$RItycxFHhUrZutxi$a4fe89493b8f30dcd38058e8d92a8aa508a5e49bb5a8141d5db70bc839822d3e	Лебедев Сергей Игоревич	dean.fit@vitte.local	4	1	t	{}	2026-11-23 23:08:57.542956	\N
5	dean_feu	pbkdf2:sha256:1000000$IKmCZv69g5Ye9QIb$bb04722b322a4df20d65fd013bf6e2d01aaf18c176045ba3a1f2b734526bbbcf	Миронова Елена Павловна	dean.feu@vitte.local	4	2	t	{}	2026-11-23 23:08:57.542956	\N
6	dean_law	pbkdf2:sha256:1000000$roUWpj8kcNsFD4QG$aede6d2508d507fa01892fb85b3f273b6368851c9965f614a8fd8f4bc5584de7	Ковалёв Дмитрий Андреевич	dean.law@vitte.local	4	3	t	{}	2026-11-23 23:08:57.542956	\N
2	rector	pbkdf2:sha256:1000000$1bsVLaOT2UU8hzPa$af16aed4b0f1eed5a2b5cf45ce6a400bc3984847d5a40b71724841e90901a618	Петров Владимир Николаевич	rector@vitte.local	2	\N	t	{}	2026-11-23 23:08:57.542956	2026-11-23 23:18:35.838083
\.


--
-- Name: academic_periods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.academic_periods_id_seq', 7, true);


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 251, true);


--
-- Name: dashboard_widgets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_widgets_id_seq', 18, true);


--
-- Name: dashboards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboards_id_seq', 5, true);


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.departments_id_seq', 10, true);


--
-- Name: directions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directions_id_seq', 12, true);


--
-- Name: faculties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.faculties_id_seq', 5, true);


--
-- Name: feedback_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.feedback_messages_id_seq', 3, true);


--
-- Name: group_performance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.group_performance_id_seq', 280, true);


--
-- Name: indicator_values_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.indicator_values_id_seq', 420, true);


--
-- Name: indicators_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.indicators_id_seq', 12, true);


--
-- Name: news_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.news_id_seq', 6, true);


--
-- Name: report_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.report_history_id_seq', 2, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.roles_id_seq', 4, true);


--
-- Name: study_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.study_groups_id_seq', 40, true);


--
-- Name: sync_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sync_log_id_seq', 3, true);


--
-- Name: uploaded_files_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.uploaded_files_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: academic_periods academic_periods_academic_year_semester_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.academic_periods
    ADD CONSTRAINT academic_periods_academic_year_semester_key UNIQUE (academic_year, semester);


--
-- Name: academic_periods academic_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.academic_periods
    ADD CONSTRAINT academic_periods_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: cache_entries cache_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cache_entries
    ADD CONSTRAINT cache_entries_pkey PRIMARY KEY (cache_key);


--
-- Name: dashboard_widgets dashboard_widgets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_widgets
    ADD CONSTRAINT dashboard_widgets_pkey PRIMARY KEY (id);


--
-- Name: dashboards dashboards_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboards
    ADD CONSTRAINT dashboards_code_key UNIQUE (code);


--
-- Name: dashboards dashboards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboards
    ADD CONSTRAINT dashboards_pkey PRIMARY KEY (id);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: directions directions_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.directions
    ADD CONSTRAINT directions_code_key UNIQUE (code);


--
-- Name: directions directions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.directions
    ADD CONSTRAINT directions_pkey PRIMARY KEY (id);


--
-- Name: faculties faculties_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_code_key UNIQUE (code);


--
-- Name: faculties faculties_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.faculties
    ADD CONSTRAINT faculties_pkey PRIMARY KEY (id);


--
-- Name: feedback_messages feedback_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feedback_messages
    ADD CONSTRAINT feedback_messages_pkey PRIMARY KEY (id);


--
-- Name: group_performance group_performance_group_id_period_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_performance
    ADD CONSTRAINT group_performance_group_id_period_id_key UNIQUE (group_id, period_id);


--
-- Name: group_performance group_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_performance
    ADD CONSTRAINT group_performance_pkey PRIMARY KEY (id);


--
-- Name: indicator_values indicator_values_indicator_id_period_id_faculty_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator_values
    ADD CONSTRAINT indicator_values_indicator_id_period_id_faculty_id_key UNIQUE (indicator_id, period_id, faculty_id);


--
-- Name: indicator_values indicator_values_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator_values
    ADD CONSTRAINT indicator_values_pkey PRIMARY KEY (id);


--
-- Name: indicators indicators_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicators
    ADD CONSTRAINT indicators_code_key UNIQUE (code);


--
-- Name: indicators indicators_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicators
    ADD CONSTRAINT indicators_pkey PRIMARY KEY (id);


--
-- Name: integration_settings integration_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integration_settings
    ADD CONSTRAINT integration_settings_pkey PRIMARY KEY (key);


--
-- Name: news news_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_pkey PRIMARY KEY (id);


--
-- Name: report_history report_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_history
    ADD CONSTRAINT report_history_pkey PRIMARY KEY (id);


--
-- Name: roles roles_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_code_key UNIQUE (code);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: study_groups study_groups_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_groups
    ADD CONSTRAINT study_groups_name_key UNIQUE (name);


--
-- Name: study_groups study_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_groups
    ADD CONSTRAINT study_groups_pkey PRIMARY KEY (id);


--
-- Name: sync_log sync_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sync_log
    ADD CONSTRAINT sync_log_pkey PRIMARY KEY (id);


--
-- Name: uploaded_files uploaded_files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_files
    ADD CONSTRAINT uploaded_files_pkey PRIMARY KEY (id);


--
-- Name: uploaded_files uploaded_files_stored_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_files
    ADD CONSTRAINT uploaded_files_stored_name_key UNIQUE (stored_name);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_created ON public.audit_log USING btree (created_at DESC);


--
-- Name: idx_perf_period; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_perf_period ON public.group_performance USING btree (period_id);


--
-- Name: idx_report_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_report_user ON public.report_history USING btree (user_id, created_at DESC);


--
-- Name: idx_values_period_faculty; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_values_period_faculty ON public.indicator_values USING btree (period_id, faculty_id);


--
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: dashboard_widgets dashboard_widgets_dashboard_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_widgets
    ADD CONSTRAINT dashboard_widgets_dashboard_id_fkey FOREIGN KEY (dashboard_id) REFERENCES public.dashboards(id) ON DELETE CASCADE;


--
-- Name: dashboard_widgets dashboard_widgets_indicator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_widgets
    ADD CONSTRAINT dashboard_widgets_indicator_id_fkey FOREIGN KEY (indicator_id) REFERENCES public.indicators(id) ON DELETE CASCADE;


--
-- Name: departments departments_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id) ON DELETE CASCADE;


--
-- Name: directions directions_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.directions
    ADD CONSTRAINT directions_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id) ON DELETE CASCADE;


--
-- Name: group_performance group_performance_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_performance
    ADD CONSTRAINT group_performance_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.study_groups(id) ON DELETE CASCADE;


--
-- Name: group_performance group_performance_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.group_performance
    ADD CONSTRAINT group_performance_period_id_fkey FOREIGN KEY (period_id) REFERENCES public.academic_periods(id) ON DELETE CASCADE;


--
-- Name: indicator_values indicator_values_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator_values
    ADD CONSTRAINT indicator_values_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id) ON DELETE CASCADE;


--
-- Name: indicator_values indicator_values_indicator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator_values
    ADD CONSTRAINT indicator_values_indicator_id_fkey FOREIGN KEY (indicator_id) REFERENCES public.indicators(id) ON DELETE CASCADE;


--
-- Name: indicator_values indicator_values_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator_values
    ADD CONSTRAINT indicator_values_period_id_fkey FOREIGN KEY (period_id) REFERENCES public.academic_periods(id) ON DELETE CASCADE;


--
-- Name: news news_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.news
    ADD CONSTRAINT news_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: report_history report_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_history
    ADD CONSTRAINT report_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: study_groups study_groups_direction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_groups
    ADD CONSTRAINT study_groups_direction_id_fkey FOREIGN KEY (direction_id) REFERENCES public.directions(id) ON DELETE CASCADE;


--
-- Name: sync_log sync_log_started_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sync_log
    ADD CONSTRAINT sync_log_started_by_fkey FOREIGN KEY (started_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: uploaded_files uploaded_files_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.uploaded_files
    ADD CONSTRAINT uploaded_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_faculty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.faculties(id) ON DELETE SET NULL;


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict Znj74wsN0aw90GydGGC9TMbVGqTfahdZtyjL7G2D21adwgoWWvsZww3URXttGh1

