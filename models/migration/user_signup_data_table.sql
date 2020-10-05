--
-- Name: user_signup_data; Type: TABLE; Schema: public; Owner: vfobhheluegnpw
--

CREATE TABLE public.user_signup_data (
    id integer NOT NULL,
    username character(32) varying NOT NULL,
    email character(64) varying NOT NULL,
    password character(128) varying NOT NULL
);


ALTER TABLE public.user_signup_data OWNER TO vfobhheluegnpw;

--
-- Name: user_signup_data_id_seq; Type: SEQUENCE; Schema: public; Owner: vfobhheluegnpw
--

CREATE SEQUENCE public.user_signup_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_signup_data_id_seq OWNER TO vfobhheluegnpw;

--
-- Name: user_signup_data id; Type: DEFAULT; Schema: public; Owner: vfobhheluegnpw
--

ALTER TABLE ONLY public.user_signup_data ALTER COLUMN id SET DEFAULT nextval('public.user_signup_data_id_seq'::regclass);

--
-- Name: user_signup_data user_signup_data_pkey; Type: CONSTRAINT; Schema: public; Owner: vfobhheluegnpw
--

ALTER TABLE ONLY public.user_signup_data ADD CONSTRAINT user_signup_data_pkey PRIMARY KEY (id);

--
-- Name: user_signup_data; Type: TABLE; Schema: public; Owner: vfobhheluegnpw
--
DROP TABLE IF EXIST public.user_signup_data;
