--
-- Name: user_channel; Type: TABLE; Schema: public; Owner: vfobhheluegnpw
--

CREATE TABLE public.user_channel (
    id integer NOT NULL,
    channel character varying(50) NOT NULL,
    description text NOT NULL,
    u_id integer NOT NULL
);


ALTER TABLE public.user_channel OWNER TO vfobhheluegnpw;

--
-- Name: user_channel_id_seq; Type: SEQUENCE; Schema: public; Owner: vfobhheluegnpw
--

CREATE SEQUENCE public.user_channel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_channel_id_seq OWNER TO vfobhheluegnpw;

--
-- Name: user_channel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vfobhheluegnpw
--

ALTER SEQUENCE public.user_channel_id_seq OWNED BY public.user_channel.id;

--
-- Name: user_channel id; Type: DEFAULT; Schema: public; Owner: vfobhheluegnpw
--

ALTER TABLE ONLY public.user_channel ALTER COLUMN id SET DEFAULT nextval('public.user_channel_id_seq'::regclass);
