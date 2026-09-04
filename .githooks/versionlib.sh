# versionlib.sh — shared logic for the alfazen-versioning hooks.
# Contract: the root VERSION file holds v{m.n.p}+{yymmddc} (or legacy -{yymmddc})
# where yymmddc is a six-digit UTC date plus one lowercase counter character (1-9 then a-z).

VERSION_FILE=VERSION
IDENT_RE='^v[0-9]+\.[0-9]+\.[0-9]+[+-][0-9]{6}[0-9a-z]$'

die() {
  echo "alfazen-versioning: $*" >&2
  exit 1
}

utc_yymmdd() {
  TZ=UTC LC_ALL=C date -u +%y%m%d
}

# read_version — print the current identifier from the root VERSION file.
read_version() {
  [ -f "$VERSION_FILE" ] || die "root $VERSION_FILE file is missing"
  id=$(tr -d '\r\n\t ' < "$VERSION_FILE")
  [ -n "$id" ] || die "$VERSION_FILE is empty"
  printf '%s\n' "$id"
}

# validate_identifier ID — die unless ID is well-formed, calendar-valid,
# and not future-dated relative to today's UTC date.
validate_identifier() {
  id=$1
  printf '%s' "$id" | grep -Eq "$IDENT_RE" ||
    die "malformed identifier '$id' in $VERSION_FILE (expected v{m.n.p}+{yymmddc})"

  case $id in
    *+*) build=${id#*+} ;;
    *-*) build=${id#*-} ;;
  esac

  bdate=${build%?}
  yy=${bdate%????}
  mm=${bdate#??}
  mm=${mm%??}
  dd=${bdate#????}
  fy=$((2000 + ${yy#0} + 0))

  case $mm in
    01|02|03|04|05|06|07|08|09|10|11|12) ;;
    *) die "invalid month in '$id'" ;;
  esac

  dim=31
  case $mm in
    04|06|09|11) dim=30 ;;
    02)
      if [ $((fy % 4)) -eq 0 ] && { [ $((fy % 100)) -ne 0 ] || [ $((fy % 400)) -eq 0 ]; }; then
        dim=29
      else
        dim=28
      fi
      ;;
  esac
  dd_n=${dd#0}; dd_n=${dd_n:-0}
  [ "$dd_n" -ge 1 ] && [ "$dd_n" -le "$dim" ] || die "invalid calendar date in '$id'"

  today=$(utc_yymmdd)
  [ "$bdate" -le "$today" ] || die "future-dated BUILD '$bdate' in '$id' (today is $today)"
}

# next_identifier OLD TODAY — print the single successor of OLD.
# In SemVer 2.0.0, the base version (v{m.n.p}) remains constant across commits;
# only the daily build counter increments.
next_identifier() {
  old=$1
  today=$2

  case $old in
    *+*) ver=${old%+*}; build=${old#*+} ;;
    *-*) ver=${old%-*}; build=${old#*-} ;;
  esac

  bdate=${build%?}
  bctr=${build#??????}

  # advance the daily counter; reset to 1 when the UTC date changes
  if [ "$bdate" != "$today" ]; then
    nctr=1
  else
    case $bctr in
      [1-8]) nctr=$((bctr + 1)) ;;
      9)     nctr=a ;;
      [a-y]) nctr=$(printf '%s' "$bctr" | tr 'a-y' 'b-z') ;;
      z)     die "daily counter exhausted ('z' already used on $today); commit rejected until the UTC date changes" ;;
      *)     die "invalid daily counter '$bctr' in '$old'" ;;
    esac
  fi

  # Output standard SemVer 2.0.0 build metadata using '+'
  printf '%s+%s%s\n' "$ver" "$today" "$nctr"
}
